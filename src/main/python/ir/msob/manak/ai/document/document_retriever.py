import logging
from typing import List, Optional

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.beans.embedder_configuration import EmbedderConfiguration
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.document.beans.document_chunk_configuration import DocumentChunkConfiguration
from src.main.python.ir.msob.manak.ai.document.beans.document_overview_configuration import DocumentOverviewConfiguration
from src.main.python.ir.msob.manak.ai.document.model.document_chunk_response import DocumentChunkResponse
from src.main.python.ir.msob.manak.ai.document.model.document_overview_response import DocumentOverviewResponse
from src.main.python.ir.msob.manak.ai.document.model.document_query_response import DocumentQueryResponse
from src.main.python.ir.msob.manak.ai.document.model.document_query_request import DocumentQueryRequest

logger = logging.getLogger(__name__)


class DocumentMultiStageRetriever:
    """
    Multi-stage retrieval pipeline:
    1️⃣ Embed query
    2️⃣ Search document overviews
    3️⃣ Retrieve relevant chunks per overview
    4️⃣ Rerank chunks using CrossEncoder
    5️⃣ Summarize top-ranked content
    """

    def __init__(self):
        self.config = ConfigConfiguration().get_properties()
        self.embedder = EmbedderConfiguration.get_embedder()
        self.overview_retriever = DocumentOverviewConfiguration.get_retriever()
        self.chunk_retriever = DocumentChunkConfiguration.get_retriever()
        self.cross_encoder = DocumentChunkConfiguration.get_cross()
        self.hybrid_summarizer = DocumentChunkConfiguration.get_hybrid_summarizer()

    # ------------------------ Public API ------------------------

    def overview_query(self, query_request: DocumentQueryRequest) -> DocumentOverviewResponse:
        logger.info(f"🔍 Overview query started: '{query_request.query}'")
        try:
            query_emb = self._embed_query(query_request.query)
            overviews = self._search_overviews(query_request.document_ids, query_emb, query_request.top_k)

            if not overviews:
                logger.warning("⚠️ No overviews retrieved for query.")
                return self._empty_overview_response(query_request)

            return self._build_overview_response(query_request, overviews)

        except Exception as e:
            logger.exception(f"❌ Overview retrieval pipeline failed: {e}")
            return self._empty_overview_response(query_request)

    def chunk_query(self, query_request: DocumentQueryRequest) -> DocumentChunkResponse:
        logger.info(f"🔍 Chunk query started: '{query_request.query}'")
        try:
            query_emb = self._embed_query(query_request.query)
            all_chunks = self._retrieve_chunks(query_request.document_ids, query_emb, query_request.top_k)

            if not all_chunks:
                logger.warning("⚠️ No chunks retrieved for matching documents.")
                return self._empty_chunk_response(query_request)

            reranked_chunks = self._rerank(query_request.query, all_chunks)
            if not reranked_chunks:
                logger.warning("⚠️ No chunks after reranking.")
                return self._empty_chunk_response(query_request)

            summary = self._summarize(reranked_chunks)
            return self._build_chunk_response(query_request, reranked_chunks, summary)

        except Exception as e:
            logger.exception(f"❌ Chunk retrieval pipeline failed: {e}")
            return self._empty_chunk_response(query_request)

    # ------------------------ Internal Steps ------------------------

    def _embed_query(self, query: str):
        logger.debug("🟢 Embedding query...")
        query_doc = Document(content=query)
        result = self.embedder.run(documents=[query_doc])
        emb = result["documents"][0].embedding
        logger.debug("✅ Query embedding created.")
        return emb

    def _search_overviews(self, doc_ids: Optional[set[str]], query_emb, top_k: int) -> List[Document]:
        logger.debug("🟢 Searching document overviews...")

        if doc_ids is None:
            self.overview_retriever.filters = {"field": "type", "operator": "in", "value": ["overview"]}
        else:
            self.overview_retriever.filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "doc_id", "operator": "in", "value": list(doc_ids)},
                    {"field": "type", "operator": "in", "value": ["overview"]},
                ],
            }

        result = self.overview_retriever.run(query_embedding=query_emb, top_k=top_k)
        docs = result.get("documents", [])
        logger.info(f"✅ Found {len(docs)} overview(s).")
        return docs

    def _retrieve_chunks(self, doc_ids: Optional[set[str]], query_emb, top_k: int) -> List[Document]:
        all_chunks = []

        if doc_ids is None:
            self.chunk_retriever.filters = {"field": "type", "operator": "in", "value": ["chunk"]}
        else:
            self.chunk_retriever.filters = {
                "operator": "AND",
                "conditions": [
                    {"field": "doc_id", "operator": "in", "value": list(doc_ids)},
                    {"field": "type", "operator": "in", "value": ["chunk"]},
                ],
            }

        result = self.chunk_retriever.run(query_embedding=query_emb, top_k=top_k)
        docs = result.get("documents", [])
        all_chunks.extend(docs)

        # deduplicate by id
        unique_chunks = list({d.id: d for d in all_chunks}.values())
        logger.info(f"✅ Retrieved {len(unique_chunks)} unique chunks.")
        return unique_chunks

    def _rerank(self, query: str, docs: List[Document]) -> List[Document]:
        if not docs:
            return []

        logger.debug("🟢 Reranking candidate chunks...")
        pairs = [(query, d.content[:512]) for d in docs if d.content]
        scores = self.cross_encoder.predict(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        top_k = self.config.application.milvus.document.chunk.retriever.rerank_top_k
        reranked = [d for d, _ in ranked[:min(top_k, len(ranked))]]
        logger.info(f"✅ Selected top {len(reranked)} chunks after reranking.")
        return reranked

    def _summarize(self, docs: List[Document]) -> str:
        if not docs:
            return ""
        logger.debug("🟢 Summarizing top-ranked chunks...")
        text = "\n\n".join(d.content for d in docs if d.content)
        try:
            summary = self.hybrid_summarizer.summarize(text)
            logger.info(f"✅ Summary generated (length: {len(summary)} chars).")
            return summary
        except Exception as e:
            logger.exception(f"⚠️ Hybrid summarizer failed: {e}")
            return text[:5000]  # fallback: truncate to first 5000 chars

    # ------------------------ Response Builders ------------------------

    @staticmethod
    def _build_overview_response(request: DocumentQueryRequest, overviews: List[Document]) -> DocumentOverviewResponse:
        overviews_res = [DocumentQueryResponse(document_id=o.id, content=o.content, meta=o.meta) for o in overviews]
        return DocumentOverviewResponse(
            document_ids=request.document_ids,
            query=request.query,
            top_k=request.top_k,
            overviews=overviews_res,
        )

    @staticmethod
    def _build_chunk_response(request: DocumentQueryRequest, chunks: List[Document],
                              summary: str) -> DocumentChunkResponse:
        chunks_res = [DocumentQueryResponse(document_id=d.id, content=d.content, meta=d.meta) for d in chunks]
        return DocumentChunkResponse(
            document_ids=request.document_ids,
            query=request.query,
            top_k=request.top_k,
            top_chunks=chunks_res,
            final_summary=summary,
        )

    @staticmethod
    def _empty_overview_response(request: DocumentQueryRequest) -> DocumentOverviewResponse:
        return DocumentOverviewResponse(
            document_ids=request.document_ids,
            query=request.query,
            top_k=request.top_k,
            overviews=[]
        )

    @staticmethod
    def _empty_chunk_response(request: DocumentQueryRequest) -> DocumentChunkResponse:
        return DocumentChunkResponse(
            document_ids=request.document_ids,
            query=request.query,
            top_k=request.top_k,
            top_chunks=[],
            final_summary=""
        )
