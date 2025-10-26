import asyncio
import logging
import os
from typing import Optional

from fastapi import HTTPException

from src.main.python.ir.msob.manak.ai.client.dms.dms_client_configuration import DmsClientConfiguration
from src.main.python.ir.msob.manak.ai.client.dms.document_dto import DocumentDto, Attachment
from src.main.python.ir.msob.manak.ai.document.document_indexer import DocumentIndexer
from src.main.python.ir.msob.manak.ai.document.document_retriever import DocumentMultiStageRetriever
from src.main.python.ir.msob.manak.ai.document.model.document_chunk_response import DocumentChunkResponse
from src.main.python.ir.msob.manak.ai.document.model.document_overview_response import DocumentOverviewResponse
from src.main.python.ir.msob.manak.ai.document.model.document_query_request import DocumentQueryRequest
from src.main.python.ir.msob.manak.ai.document.model.document_request import DocumentRequest
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".docx", ".html"}


class DocumentService:
    """
    Service responsible for document operations:
    - Downloading and indexing documents
    - Querying and retrieving information in multi-stage fashion
    """

    def __init__(self):
        self.indexer = DocumentIndexer()
        self.dms_client = DmsClientConfiguration().get_dms_client()
        self.searcher: Optional[DocumentMultiStageRetriever] = None
        self._initialize_searcher()

    # ---------- Initialization ----------
    def _initialize_searcher(self):
        """Initialize the multi-stage retriever with safe error handling."""
        try:
            self.searcher = DocumentMultiStageRetriever()
            logger.info("✅ MultiStageRetriever initialized successfully.")
        except Exception as e:
            logger.exception("❌ Failed to initialize MultiStageRetriever: %s", e)
            self.searcher = None

    # ---------- Add Document ----------
    async def add(self, dto: DocumentRequest) -> DocumentResponse:
        """
        Downloads a document (from file path or URL) and indexes it.

        Logs each step of the process for traceability.
        """
        logger.info("📥 Add document request started: document_id=%s", dto.document_id)

        try:
            # Fetch document metadata
            document: DocumentDto = await self.dms_client.get_document(dto.document_id)
            attachment: Attachment = dto.get_latest_attachment()
            logger.info("✅ Document fetched successfully: document_id=%s, attachment=%s",
                        document.document_id, attachment.file_path)

            # Determine file extension
            if "." not in attachment.file_name:
                raise HTTPException(status_code=400, detail="Cannot determine file extension from file name")
            _, ext = os.path.splitext(attachment.file_name)

            if ext.lower() not in SUPPORTED_EXTENSIONS:
                logger.warning("⚠️ Unsupported file type '%s' for document '%s'", ext, document.document_id)
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(SUPPORTED_EXTENSIONS)}"
                )

            logger.info("📄 Processing file '%s' with extension '%s'", attachment.file_name, ext)

            # Download file asynchronously
            file_content = await self.dms_client.download_file(attachment.file_path)
            logger.info("✅ File downloaded successfully (%d bytes)", len(file_content))

            # Index the content in a background thread
            loop = asyncio.get_event_loop()
            result: DocumentResponse = await loop.run_in_executor(None, self.indexer.index, document, None, file_content)

            logger.info("🧩 Document indexed successfully: document_id=%s", result.document_id)
            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("❌ Failed to process document '%s': %s", dto.document_id, e)
            raise RuntimeError(f"Document indexing failed: {str(e)}") from e

    # ---------- Overview Query ----------
    def overview_query(self, query_request: DocumentQueryRequest) -> DocumentOverviewResponse:
        """
        Executes a multi-stage overview query on documents.

        Logs query text, top_k value, and number of returned overviews.
        """
        if not self.searcher:
            logger.error("❌ Searcher not initialized for overview query.")
            raise RuntimeError("Searcher not initialized.")

        try:
            logger.info("🔍 Overview query started: query='%s' (top_k=%d)", query_request.query, query_request.top_k)
            response: DocumentOverviewResponse = self.searcher.overview_query(query_request)
            logger.info("✅ Overview query completed: returned %d overviews", len(response.overviews))
            if not response.overviews:
                logger.warning("⚠️ Overview query returned no results for query='%s'", query_request.query)
            return response

        except Exception as e:
            logger.exception("❌ Overview query execution failed: %s", e)
            raise RuntimeError(f"Overview query execution failed: {str(e)}") from e

    # ---------- Chunk Query ----------
    def chunk_query(self, query_request: DocumentQueryRequest) -> DocumentChunkResponse:
        """
        Executes a multi-stage chunk-level query on documents.

        Logs query text, top_k value, and number of returned chunks.
        """
        if not self.searcher:
            logger.error("❌ Searcher not initialized for chunk query.")
            raise RuntimeError("Searcher not initialized.")

        try:
            logger.info("🔎 Chunk query started: query='%s' (top_k=%d)", query_request.query, query_request.top_k)
            response: DocumentChunkResponse = self.searcher.chunk_query(query_request)
            logger.info("✅ Chunk query completed with %d top chunks.", len(response.top_chunks))
            if not response.top_chunks:
                logger.warning("⚠️ Chunk query returned no results for query='%s'", query_request.query)
            return response

        except Exception as e:
            logger.exception("❌ Chunk query execution failed: %s", e)
            raise RuntimeError(f"Chunk query execution failed: {str(e)}") from e
