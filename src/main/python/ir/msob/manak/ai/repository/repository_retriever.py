import logging
from typing import List, Set, Optional
from haystack.dataclasses import Document
from pydantic import ValidationError
from src.main.python.ir.msob.manak.ai.beans.embedder_configuration import EmbedderConfiguration
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.repository.beans.repository_chunk_configuration import \
    RepositoryChunkConfiguration
from src.main.python.ir.msob.manak.ai.repository.beans.repository_overview_configuration import \
    RepositoryOverviewConfiguration
from src.main.python.ir.msob.manak.ai.repository.model.repository_chunk_response import RepositoryChunkResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_overview_response import RepositoryOverviewResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_request import RepositoryQueryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_response import RepositoryQueryResponse

logger = logging.getLogger(__name__)

class RepositoryMultiStageRetriever:
    """
    Multi-stage retriever specialized for repositories.

    Steps:
      1) Embed query
      2) Search repository overviews (filtered by repository_id if provided)
      3) Retrieve chunks for matching repository_id(s)
      4) Rerank chunks with CrossEncoder
      5) Summarize top chunks with hybrid summarizer
    """

    def __init__(self):
        self.config = ConfigConfiguration().get_properties()
        self.embedder = EmbedderConfiguration.get_embedder()
        # retrievers + models come from repository-specific configurations
        self.overview_retriever = RepositoryOverviewConfiguration.get_retriever()
        self.chunk_retriever = RepositoryChunkConfiguration.get_retriever()
        self.cross_encoder = RepositoryChunkConfiguration.get_cross()
        # summarizer for final answer (based on chunks)
        self.hybrid_summarizer = RepositoryChunkConfiguration.get_hybrid_summarizer()

    # ---------------- Public API ----------------

    def overview_query(self, request: RepositoryQueryRequest) -> RepositoryOverviewResponse:
        """
        request must provide:
          - query: str
          - top_k: int
          - repository_id: Optional[str] (if provided, results limited to that repo)
        """
        logger.info("🔍 Repository multi-stage retrieval started for query='%s' repo='%s'",
                    getattr(request, "query", None), getattr(request, "repository_id", None))

        try:
            query_emb = self._embed_query(request.query)

            overviews = self._search_overviews(request.repository_ids, query_emb, request.top_k)
            if not overviews:
                logger.warning("No repository overviews found for query.")
                return self._empty_overview_response(request)

            return self._build_overview_response(request, overviews)

        except Exception as e:
            logger.exception("Repository retrieval pipeline failed: %s", e)
            raise

    def chunk_query(self, request: RepositoryQueryRequest) -> RepositoryChunkResponse:
        """
        request must provide:
          - query: str
          - top_k: int
          - repository_id: Optional[str] (if provided, results limited to that repo)
        """
        logger.info("🔍 Repository multi-stage retrieval started for query='%s' repo='%s'",
                    request.query, request.repository_ids)

        try:
            query_emb = self._embed_query(request.query)

            all_chunks = self._retrieve_chunks(request.repository_ids, query_emb, request.top_k)
            if not all_chunks:
                logger.warning("No chunks retrieved for repositories: %s", request.repository_ids)
                return self._empty_chunk_response(request)

            reranked = self._rerank(request.query, all_chunks)
            if not reranked:
                logger.warning("Reranking returned no candidates.")
                return self._empty_chunk_response(request)

            summary = self._summarize(reranked)

            return self._build_chunk_response(request, reranked, summary)

        except Exception as e:
            logger.exception("Repository retrieval pipeline failed: %s", e)
            raise

    # ---------------- Internal Steps ----------------

    def _embed_query(self, query: str):
        logger.debug("Embedding repository query text...")
        qdoc = Document(content=query)
        result = self.embedder.run(documents=[qdoc])
        emb = result["documents"][0].embedding
        logger.debug("Query embedding ready.")
        return emb

    def _search_overviews(self, repository_ids: Optional[set[str]], query_emb, top_k: int) -> List[Document]:
        """
        Search overview collection. If repository_id provided, include it in filters.
        """
        logger.debug("Searching repository overviews (top_k=%d) repo_id=%s", top_k, repository_ids)

        # Build filters: always require type == overview
        if repository_ids is None:
            # only overview type
            self.overview_retriever.filters = {"field": "type", "operator": "in", "value": ["overview"]}
        else:
            # AND both conditions
            self.overview_retriever.filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "type", "operator": "in", "value": ["overview"]},
                    {"field": "repository_id", "operator": "in", "value": [repository_ids]}
                ]
            }

        res = self.overview_retriever.run(query_embedding=query_emb, top_k=top_k)
        docs = res.get("documents", [])
        logger.info("Found %d overview(s).", len(docs))
        return docs

    def _collect_repo_ids(self, overviews: List[Document]) -> Set[str]:
        ids = set()
        for o in overviews:
            meta = getattr(o, "meta", {}) or {}
            rid = meta.get("repository_id") or meta.get("repo_id") or meta.get("doc_id") or None
            if not rid and o.id:
                # try to parse id convention "<repo>_overview"
                if isinstance(o.id, str) and o.id.endswith("_overview"):
                    ids.add(o.id.replace("_overview", ""))
                continue
            if rid:
                ids.add(rid)
        logger.debug("Collected repository ids from overviews: %s", ids)
        return ids

    def _retrieve_chunks(self, repo_ids: Optional[set[str]] , query_emb, top_k: int) -> List[Document]:
        """
        Retrieve chunks for the set of repository ids.
        We run the chunk_retriever once per repo_id and aggregate results.
        """
        all_chunks = []
        logger.debug("Retrieving chunks for repo_ids=%s (top_k=%d)", repo_ids, top_k)
        if  repo_ids is None:
            self.chunk_retriever.filters = {"field": "type", "operator": "in", "value": ["chunk"]}
        else:
            self.chunk_retriever.filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "repository_id", "operator": "in", "value": [repo_ids]},
                    {"field": "type", "operator": "in", "value": ["chunk"]}
                ]
            }
        res = self.chunk_retriever.run(query_embedding=query_emb, top_k=top_k)
        docs = res.get("documents", [])
        logger.debug("Retrieved %d chunks for repo %s", len(docs), repo_ids)
        all_chunks.extend(docs)

        # deduplicate by id preserving last seen
        unique = {}
        for d in all_chunks:
            if getattr(d, "id", None):
                unique[d.id] = d
        deduped = list(unique.values())
        logger.info("Total unique chunks retrieved: %d", len(deduped))
        return deduped

    def _rerank(self, query: str, docs: List[Document]) -> List[Document]:
        if not docs:
            return []
        logger.debug("Preparing pairs for cross-encoder reranking (limit content to 512 chars).")
        pairs = [(query, (d.content or "")[:512]) for d in docs if getattr(d, "content", None)]
        try:
            scores = self.cross_encoder.predict(pairs)
        except Exception as e:
            logger.exception("Cross-encoder prediction failed: %s", e)
            # If cross-encoder fails, fallback to original order
            return docs[: self._rerank_top_k(len(docs))]

        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        top_n = self._rerank_top_k(len(ranked))
        reranked = [d for d, _ in ranked[:top_n]]
        logger.info("Reranking completed. Selected top %d chunks.", len(reranked))
        return reranked

    def _rerank_top_k(self):
        # kept for compatibility if needed
        return self._rerank_top_k(1)

    def _rerank_top_k(self, default_len: int) -> int:
        """
        Read rerank_top_k from config if available, else default to min(10, n)
        path used: self.config.application.milvus.repository.chunk.retriever.rerank_top_k
        """
        try:
            val = int(self.config.application.milvus.repository.chunk.retriever.rerank_top_k)
            return val
        except Exception:
            return min(10, default_len)

    def _summarize(self, docs: List[Document]) -> str:
        if not docs:
            return ""
        logger.debug("Summarizing top-ranked chunks into final summary.")
        text = "\n\n".join([d.content for d in docs if getattr(d, "content", None)])
        try:
            summary = self.hybrid_summarizer.summarize(text)
            logger.info("Summary generated (chars=%d).", len(summary))
            return summary
        except Exception as e:
            logger.exception("Hybrid summarizer failed: %s", e)
            # fallback to truncated concatenation
            return text[:4000]

    # ---------------- Response Builders ----------------

    def _build_overview_response(self, request: RepositoryQueryRequest, overviews: List[Document]) -> RepositoryOverviewResponse:
        """
        Build RepositoryQueryResponse using RepositoryResponse as element model.
        Map haystack.Document -> RepositoryResponse (document-level fields + repo metadata where available).
        Skip documents that raise validation errors and log them.
        """
        overviews_res: List[RepositoryQueryResponse] = []
        repo_ids = []

        # Helper to map a haystack Document to RepositoryResponse
        def map_doc_to_repo_response(doc: Document, kind: str) -> RepositoryQueryResponse:
            meta = getattr(doc, "meta", {}) or {}
            # try to extract common chunk fields
            file_path = meta.get("file_path") or meta.get("path") or None
            file_name = meta.get("file_name") or (file_path and file_path.split("/")[-1]) or None
            chunk_idx = meta.get("chunk_index")
            total_chunks = meta.get("total_chunks")

            payload = {
                # repo-level possibly present in meta
                "repository_id": meta.get("repository_id"),
                "branch": meta.get("branch"),
                "overview_id": meta.get("overview_id"),
                # document-level
                "document_id": getattr(doc, "id", None),
                "content": getattr(doc, "content", None),
                "meta": meta,
                "score": getattr(doc, "score", None),
                "file_path": file_path,
                "file_name": file_name,
                "chunk_index": chunk_idx,
                "total_chunks": total_chunks,
                "type": kind,
            }
            return RepositoryQueryResponse(**payload)

        # Convert overviews
        for o in overviews:
            try:
                rr = map_doc_to_repo_response(o, kind="overview")
                # collect repo id
                if rr.repository_id:
                    repo_ids.append(rr.repository_id)
                else:
                    # fallback: parse document_id like "<repo>_overview"
                    did = rr.document_id
                    if isinstance(did, str) and did.endswith("_overview"):
                        repo_ids.append(did.replace("_overview", ""))
                overviews_res.append(rr)
            except ValidationError as ve:
                logger.exception("Skipping overview due validation error: %s doc_id=%s", ve, getattr(o, "id", None))
            except Exception as e:
                logger.exception("Unexpected error mapping overview doc_id=%s: %s", getattr(o, "id", None), e)

        resp = RepositoryOverviewResponse(
            repository_ids=request.repository_ids,
            query=request.query,
            top_k=request.top_k,
            overviews=overviews_res,
        )
        return resp

    def _build_chunk_response(self, request: RepositoryQueryRequest, chunks: List[Document],
                                 summary: str) -> RepositoryChunkResponse:
        """
        Build RepositoryQueryResponse using RepositoryResponse as element model.
        Map haystack.Document -> RepositoryResponse (document-level fields + repo metadata where available).
        Skip documents that raise validation errors and log them.
        """
        chunks_res: List[RepositoryQueryResponse] = []
        repo_ids = []

        # Helper to map a haystack Document to RepositoryResponse
        def map_doc_to_repo_response(doc: Document, kind: str) -> RepositoryQueryResponse:
            meta = getattr(doc, "meta", {}) or {}
            # try to extract common chunk fields
            file_path = meta.get("file_path") or meta.get("path") or None
            file_name = meta.get("file_name") or (file_path and file_path.split("/")[-1]) or None
            chunk_idx = meta.get("chunk_index")
            total_chunks = meta.get("total_chunks")

            payload = {
                # repo-level possibly present in meta
                "repository_id": meta.get("repository_id"),
                "branch": meta.get("branch"),
                "overview_id": meta.get("overview_id"),
                # document-level
                "document_id": getattr(doc, "id", None),
                "content": getattr(doc, "content", None),
                "meta": meta,
                "score": getattr(doc, "score", None),
                "file_path": file_path,
                "file_name": file_name,
                "chunk_index": chunk_idx,
                "total_chunks": total_chunks,
                "type": kind,
            }
            return RepositoryQueryResponse(**payload)

        # Convert chunks
        for d in chunks:
            try:
                rr = map_doc_to_repo_response(d, kind="chunk")
                chunks_res.append(rr)
            except ValidationError as ve:
                logger.exception("Skipping chunk due validation error: %s doc_id=%s", ve, getattr(d, "id", None))
            except Exception as e:
                logger.exception("Unexpected error mapping chunk doc_id=%s: %s", getattr(d, "id", None), e)

        resp = RepositoryChunkResponse(
            repository_ids=request.repository_ids,
            query=request.query,
            top_k=request.top_k,
            top_chunks=chunks_res,
            final_summary=summary,
        )
        return resp

    def _empty_chunk_response(self, request: RepositoryQueryRequest) -> RepositoryChunkResponse:
        return RepositoryChunkResponse(
            repository_ids=request.repository_ids,
            query=request.query,
            top_k=request.top_k,
            top_chunks=[],
            final_summary="",
        )

    def _empty_overview_response(self, request: RepositoryQueryRequest) -> RepositoryOverviewResponse:
        return  RepositoryOverviewResponse(
            repository_ids=request.repository_ids,
            query=request.query,
            top_k=request.top_k,
            overviews=[],
        )