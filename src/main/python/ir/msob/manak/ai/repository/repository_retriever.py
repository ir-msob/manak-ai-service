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
    """

    def __init__(self):
        self.config = ConfigConfiguration().get_properties()
        self.embedder = EmbedderConfiguration.get_embedder()
        self.overview_retriever = RepositoryOverviewConfiguration.get_retriever()
        self.chunk_retriever = RepositoryChunkConfiguration.get_retriever()
        self.cross_encoder = RepositoryChunkConfiguration.get_cross()
        self.hybrid_summarizer = RepositoryChunkConfiguration.get_hybrid_summarizer()

    # ---------------- Public API ----------------

    def overview_query(self, request: RepositoryQueryRequest) -> RepositoryOverviewResponse:
        logger.info(
            "🔍 Repository multi-stage retrieval started for query='%s', repo_ids=%s, top_k=%d",
            request.query, request.repository_ids, request.top_k
        )
        try:
            query_emb = self._embed_query(request.query)
            overviews = self._search_overviews(request.repository_ids, query_emb, request.top_k)

            if not overviews:
                logger.warning("No repository overviews found for query='%s'", request.query)
                return self._empty_overview_response(request)

            response = self._build_overview_response(request, overviews)
            logger.info("✅ Overview retrieval completed. Total overviews=%d", len(response.overviews))
            return response

        except Exception as e:
            logger.exception("Repository overview retrieval pipeline failed: %s", e)
            raise

    def chunk_query(self, request: RepositoryQueryRequest) -> RepositoryChunkResponse:
        logger.info(
            "🔍 Repository multi-stage retrieval started for query='%s', repo_ids=%s, top_k=%d",
            request.query, request.repository_ids, request.top_k
        )
        try:
            query_emb = self._embed_query(request.query)
            all_chunks = self._retrieve_chunks(request.repository_ids, query_emb, request.top_k)

            if not all_chunks:
                logger.warning("No chunks retrieved for query='%s' repo_ids=%s", request.query, request.repository_ids)
                return self._empty_chunk_response(request)

            reranked = self._rerank(request.query, all_chunks)
            if not reranked:
                logger.warning("Reranking returned no candidates for query='%s'", request.query)
                return self._empty_chunk_response(request)

            summary = self._summarize(reranked)
            response = self._build_chunk_response(request, reranked, summary)
            logger.info("✅ Chunk retrieval completed. Total chunks=%d", len(response.top_chunks))
            return response

        except Exception as e:
            logger.exception("Repository chunk retrieval pipeline failed: %s", e)
            raise

    # ---------------- Internal Steps ----------------

    def _embed_query(self, query: str):
        logger.debug("Embedding repository query text...")
        qdoc = Document(content=query)
        result = self.embedder.run(documents=[qdoc])
        emb = result["documents"][0].embedding
        logger.debug("Query embedding ready (dim=%d).", len(emb))
        return emb

    def _search_overviews(self, repository_ids: Optional[set[str]], query_emb, top_k: int) -> List[Document]:
        logger.debug("Searching repository overviews (top_k=%d) repo_ids=%s", top_k, repository_ids)

        if repository_ids is None:
            self.overview_retriever.filters = {"field": "type", "operator": "in", "value": ["overview"]}
        else:
            self.overview_retriever.filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "type", "operator": "in", "value": ["overview"]},
                    {"field": "repository_id", "operator": "in", "value": [repository_ids]}
                ]
            }

        res = self.overview_retriever.run(query_embedding=query_emb, top_k=top_k)
        docs = res.get("documents", [])
        if repository_ids and not docs:
            logger.warning("No overviews found for specified repository_ids=%s", repository_ids)
        logger.info("Found %d overview(s).", len(docs))
        return docs

    def _collect_repo_ids(self, overviews: List[Document]) -> Set[str]:
        ids = set()
        for o in overviews:
            meta = getattr(o, "meta", {}) or {}
            rid = meta.get("repository_id") or meta.get("repo_id") or meta.get("doc_id") or None
            if not rid and o.id and isinstance(o.id, str) and o.id.endswith("_overview"):
                ids.add(o.id.replace("_overview", ""))
            elif rid:
                ids.add(rid)
        logger.debug("Collected repository ids from overviews: %s", ids)
        return ids

    def _retrieve_chunks(self, repo_ids: Optional[set[str]], query_emb, top_k: int) -> List[Document]:
        all_chunks = []
        logger.debug("Retrieving chunks for repo_ids=%s (top_k=%d)", repo_ids, top_k)

        if repo_ids is None:
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
        logger.debug("Retrieved %d chunks for repo_ids=%s", len(docs), repo_ids)
        all_chunks.extend(docs)

        # deduplicate
        unique = {d.id: d for d in all_chunks if getattr(d, "id", None)}
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
            return docs[: self._rerank_top_k(len(docs))]

        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        top_n = self._rerank_top_k(len(ranked))
        reranked = [d for d, _ in ranked[:top_n]]
        logger.info("Reranking completed. Original=%d, Selected top=%d", len(docs), len(reranked))
        return reranked

    def _rerank_top_k(self, default_len: int) -> int:
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
            logger.warning("Hybrid summarizer failed, using fallback concatenation: %s", e)
            return text[:4000]

    # ---------------- Response Builders ----------------

    def _build_overview_response(self, request: RepositoryQueryRequest, overviews: List[Document]) -> RepositoryOverviewResponse:
        overviews_res: List[RepositoryQueryResponse] = []
        skipped_count = 0

        def map_doc_to_repo_response(doc: Document, kind: str) -> RepositoryQueryResponse:
            meta = getattr(doc, "meta", {}) or {}
            file_path = meta.get("file_path") or meta.get("path") or None
            file_name = meta.get("file_name") or (file_path and file_path.split("/")[-1]) or None
            chunk_idx = meta.get("chunk_index")
            total_chunks = meta.get("total_chunks")

            payload = {
                "repository_id": meta.get("repository_id"),
                "branch": meta.get("branch"),
                "overview_id": meta.get("overview_id"),
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

        for o in overviews:
            try:
                rr = map_doc_to_repo_response(o, kind="overview")
                overviews_res.append(rr)
            except ValidationError as ve:
                skipped_count += 1
                logger.exception("Skipping overview due to validation error: %s doc_id=%s", ve, getattr(o, "id", None))
            except Exception as e:
                skipped_count += 1
                logger.exception("Unexpected error mapping overview doc_id=%s: %s", getattr(o, "id", None), e)

        logger.info("Mapped %d overview documents successfully, skipped %d due to errors.", len(overviews_res), skipped_count)
        return RepositoryOverviewResponse(
            repository_ids=request.repository_ids,
            query=request.query,
            top_k=request.top_k,
            overviews=overviews_res,
        )

    def _build_chunk_response(self, request: RepositoryQueryRequest, chunks: List[Document], summary: str) -> RepositoryChunkResponse:
        chunks_res: List[RepositoryQueryResponse] = []
        skipped_count = 0

        def map_doc_to_repo_response(doc: Document, kind: str) -> RepositoryQueryResponse:
            meta = getattr(doc, "meta", {}) or {}
            file_path = meta.get("file_path") or meta.get("path") or None
            file_name = meta.get("file_name") or (file_path and file_path.split("/")[-1]) or None
            chunk_idx = meta.get("chunk_index")
            total_chunks = meta.get("total_chunks")

            payload = {
                "repository_id": meta.get("repository_id"),
                "branch": meta.get("branch"),
                "overview_id": meta.get("overview_id"),
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

        for d in chunks:
            try:
                rr = map_doc_to_repo_response(d, kind="chunk")
                chunks_res.append(rr)
            except ValidationError as ve:
                skipped_count += 1
                logger.exception("Skipping chunk due to validation error: %s doc_id=%s", ve, getattr(d, "id", None))
            except Exception as e:
                skipped_count += 1
                logger.exception("Unexpected error mapping chunk doc_id=%s: %s", getattr(d, "id", None), e)

        logger.info("Mapped %d chunk documents successfully, skipped %d due to errors.", len(chunks_res), skipped_count)
        return RepositoryChunkResponse(
            repository_ids=request.repository_ids,
            query=request.query,
            top_k=request.top_k,
            top_chunks=chunks_res,
            final_summary=summary,
        )

    def _empty_chunk_response(self, request: RepositoryQueryRequest) -> RepositoryChunkResponse:
        logger.info("Returning empty chunk response for query='%s' repo_ids=%s", request.query, request.repository_ids)
        return RepositoryChunkResponse(
            repository_ids=request.repository_ids,
            query=request.query,
            top_k=request.top_k,
            top_chunks=[],
            final_summary="",
        )

    def _empty_overview_response(self, request: RepositoryQueryRequest) -> RepositoryOverviewResponse:
        logger.info("Returning empty overview response for query='%s' repo_ids=%s", request.query, request.repository_ids)
        return RepositoryOverviewResponse(
            repository_ids=request.repository_ids,
            query=request.query,
            top_k=request.top_k,
            overviews=[],
        )
