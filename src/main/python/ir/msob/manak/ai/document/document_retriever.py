import logging
from typing import List

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.beans.embedder_configuration import EmbedderConfiguration
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.document.beans.document_chunk_configuration import DocumentChunkConfiguration
from src.main.python.ir.msob.manak.ai.document.beans.document_overview_configuration import \
    DocumentOverviewConfiguration
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse
from src.main.python.ir.msob.manak.ai.document.model.text_query_request import TextQueryRequest
from src.main.python.ir.msob.manak.ai.document.model.text_query_response import TextQueryResponse

logger = logging.getLogger(__name__)


class MultiStageRetriever:
    """
    Multi-stage retrieval pipeline:
    1. Embed query
    2. Search document overviews
    3. Retrieve relevant chunks per overview
    4. Rerank results using cross-encoder
    5. Summarize top-ranked content
    """

    def __init__(self, config=None):
        self.config = config or ConfigConfiguration().get_properties()
        self.embedder = EmbedderConfiguration.get_embedder()
        self.overview_retriever = DocumentOverviewConfiguration.get_retriever()
        self.chunk_retriever = DocumentChunkConfiguration.get_retriever()
        self.cross_encoder = DocumentChunkConfiguration.get_cross()
        self.hybrid_summarizer = DocumentChunkConfiguration.get_hybrid_summarizer()

    # ------------------------ Public API ------------------------

    def query_text(self, text_query_request: TextQueryRequest) -> TextQueryResponse:
        """Runs the full multi-stage retrieval pipeline."""
        logger.info(f"🔍 Starting multi-stage retrieval for query: '{text_query_request.query}'")

        try:
            query_emb = self._embed_query(text_query_request.query)

            overviews = self._search_overviews(query_emb, text_query_request.top_k)
            if not overviews:
                logger.warning("No overviews retrieved for query.")
                return self._empty_response(text_query_request)

            doc_ids = {o.meta.get("doc_id") for o in overviews if o.meta.get("doc_id")}
            if not doc_ids:
                logger.warning("No document IDs found in overviews.")
                return self._empty_response(text_query_request)

            all_chunks = self._retrieve_chunks(doc_ids, query_emb, text_query_request.top_k)
            if not all_chunks:
                logger.warning("No chunks retrieved for matching documents.")
                return self._empty_response(text_query_request)

            reranked_chunks = self._rerank(text_query_request.query, all_chunks)
            if not reranked_chunks:
                logger.warning("No reranked chunks found.")
                return self._empty_response(text_query_request)

            summary = self._summarize(reranked_chunks)

            return self._build_response(text_query_request, overviews, reranked_chunks, summary)

        except Exception as e:
            logger.exception(f"❌ Retrieval pipeline failed: {e}")
            raise

    # ------------------------ Internal Steps ------------------------

    def _embed_query(self, query: str):
        """Generate query embedding using the same embedder as documents."""
        logger.debug("Embedding query text...")
        query_doc = Document(content=query)
        result = self.embedder.run(documents=[query_doc])
        emb = result["documents"][0].embedding
        logger.debug("Query embedding created successfully.")
        return emb

    def _search_overviews(self, query_emb, top_k: int) -> List[Document]:
        """Retrieve top overview documents."""
        logger.debug("Searching document overviews...")
        self.overview_retriever.filters = {"field": "type", "operator": "in", "value": ["overview"]}
        result = self.overview_retriever.run(query_embedding=query_emb, top_k=top_k)
        docs = result.get("documents", [])
        logger.info(f"Found {len(docs)} overview(s).")
        return docs

    def _retrieve_chunks(self, doc_ids: set, query_emb, top_k: int) -> List[Document]:
        """Retrieve chunks belonging to the overview document IDs."""
        all_chunks = []
        logger.debug(f"Retrieving chunks for {len(doc_ids)} documents...")
        for doc_id in doc_ids:
            self.chunk_retriever.filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "doc_id", "operator": "in", "value": [doc_id]},
                    {"field": "type", "operator": "in", "value": ["chunk"]},
                ],
            }
            result = self.chunk_retriever.run(query_embedding=query_emb, top_k=top_k)
            docs = result.get("documents", [])
            all_chunks.extend(docs)
        logger.info(f"Retrieved {len(all_chunks)} total chunks.")
        return list({d.id: d for d in all_chunks}.values())  # dedup by id

    def _rerank(self, query: str, docs: List[Document]) -> List[Document]:
        """Rerank using CrossEncoder model."""
        if not docs:
            return []
        logger.debug("Reranking candidate chunks...")
        top_k = getattr(self.config.pipeline, "rerank_top_k", 10)
        pairs = [(query, d.content[:512]) for d in docs if d.content]
        scores = self.cross_encoder.predict(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        reranked = [d for d, _ in ranked[:min(top_k, len(ranked))]]
        logger.info(f"Selected top {len(reranked)} chunks after reranking.")
        return reranked

    def _summarize(self, docs: List[Document]) -> str:
        """Summarize the top reranked chunks into a single overview."""
        if not docs:
            return ""
        logger.debug("Summarizing top-ranked chunks...")
        text = "\n\n".join(d.content for d in docs if d.content)
        summary = self.hybrid_summarizer.summarize(text)
        logger.info(f"Summary generated with length: {len(summary)} chars.")
        return summary

    # ------------------------ Response Builders ------------------------

    @staticmethod
    def _build_response(request: TextQueryRequest,
                        overviews: List[Document],
                        chunks: List[Document],
                        summary: str) -> TextQueryResponse:
        """Builds the structured response object."""
        overviews_res = [DocumentResponse(id=o.id, content=o.content, meta=o.meta) for o in overviews]
        chunks_res = [DocumentResponse(id=d.id, content=d.content, meta=d.meta) for d in chunks]

        return TextQueryResponse(
            query=request.query,
            top_k=request.top_k,
            overviews=overviews_res,
            top_chunks=chunks_res,
            final_summary=summary,
        )

    @staticmethod
    def _empty_response(request: TextQueryRequest) -> TextQueryResponse:
        """Return an empty but valid response if no results found."""
        return TextQueryResponse(
            query=request.query,
            top_k=request.top_k,
            overviews=[],
            top_chunks=[],
            final_summary="",
        )
