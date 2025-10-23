import logging
from typing import List, Set, Optional

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.beans.embedder_configuration import EmbedderConfiguration
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.repository.beans.repository_chunk_configuration import RepositoryChunkConfiguration
from src.main.python.ir.msob.manak.ai.repository.beans.repository_overview_configuration import RepositoryOverviewConfiguration
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse
from src.main.python.ir.msob.manak.ai.document.model.document_query_request import DocumentQueryRequest
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

    def query(self, request: RepositoryQueryRequest) -> RepositoryQueryResponse:
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

            overviews = self._search_overviews(query_emb, request.top_k, getattr(request, "repository_id", None))
            if not overviews:
                logger.warning("No repository overviews found for query.")
                return self._empty_response(request)

            # collect repository ids from overview meta (fallback to overview.id)
            repo_ids = self._collect_repo_ids(overviews)
            if not repo_ids:
                logger.warning("No repository ids discovered from overviews.")
                return self._empty_response(request)

            all_chunks = self._retrieve_chunks(repo_ids, query_emb, request.top_k)
            if not all_chunks:
                logger.warning("No chunks retrieved for repositories: %s", repo_ids)
                return self._empty_response(request)

            reranked = self._rerank(request.query, all_chunks)
            if not reranked:
                logger.warning("Reranking returned no candidates.")
                return self._empty_response(request)

            summary = self._summarize(reranked)

            return self._build_response(request, overviews, reranked, summary)

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

    def _search_overviews(self, query_emb, top_k: int, repository_id: Optional[str]) -> List[Document]:
        """
        Search overview collection. If repository_id provided, include it in filters.
        """
        logger.debug("Searching repository overviews (top_k=%d) repo_id=%s", top_k, repository_id)

        # Build filters: always require type == overview
        if repository_id:
            # AND both conditions
            self.overview_retriever.filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "type", "operator": "in", "value": ["overview"]},
                    {"field": "repository_id", "operator": "in", "value": [repository_id]}
                ]
            }
        else:
            # only overview type
            self.overview_retriever.filters = {"field": "type", "operator": "in", "value": ["overview"]}

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

    def _retrieve_chunks(self, repo_ids: Set[str], query_emb, top_k: int) -> List[Document]:
        """
        Retrieve chunks for the set of repository ids.
        We run the chunk_retriever once per repo_id and aggregate results.
        """
        all_chunks = []
        logger.debug("Retrieving chunks for repo_ids=%s (top_k=%d)", repo_ids, top_k)
        for rid in repo_ids:
            self.chunk_retriever.filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "repository_id", "operator": "in", "value": [rid]},
                    {"field": "type", "operator": "in", "value": ["chunk"]}
                ]
            }
            res = self.chunk_retriever.run(query_embedding=query_emb, top_k=top_k)
            docs = res.get("documents", [])
            logger.debug("Retrieved %d chunks for repo %s", len(docs), rid)
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

    def _build_response(self, request: RepositoryQueryRequest, overviews: List[Document], chunks: List[Document], summary: str) -> RepositoryQueryResponse:
        """
        Map haystack Documents to DocumentResponse and build RepositoryQueryResponse.
        Adjust mapping if your RepositoryQueryResponse has different fields.
        """
        overviews_res: List[DocumentResponse] = [DocumentResponse(id=o.id, content=o.content, meta=o.meta) for o in overviews]
        chunks_res: List[DocumentResponse] = [DocumentResponse(id=d.id, content=d.content, meta=d.meta) for d in chunks]

        resp = RepositoryQueryResponse(**{
            "query": request.query,
            "top_k": request.top_k,
            "overviews": overviews_res,
            "top_chunks": chunks_res,
            "final_summary": summary
        })
        return resp

    def _empty_response(self, request: RepositoryQueryRequest) -> RepositoryQueryResponse:
        return RepositoryQueryResponse(**{
            "query": request.query,
            "top_k": request.top_k,
            "overviews": [],
            "top_chunks": [],
            "final_summary": ""
        })
