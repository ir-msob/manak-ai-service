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
        logger.info("📥 Add document request started: %s", dto.file_path)

        try:
            # Fetch document metadata
            document: DocumentDto = await self.dms_client.get_document(dto.document_id)
            attachment: Attachment = dto.get_latest_attachment()
            logger.info("✅ Document fetched successfully: %s", document.document_id)

            # Determine file extension
            if "." not in attachment.file_path.split("/")[-1]:
                raise HTTPException(status_code=400, detail="Cannot determine file extension from URL")
            _, ext = os.path.splitext(attachment.file_name)

            if ext.lower() not in SUPPORTED_EXTENSIONS:
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
            result: DocumentResponse = await loop.run_in_executor(None, self.indexer.index, document, file_content)

            logger.info("🧩 Document indexed successfully: %s", result.document_id)
            return result

        except Exception as e:
            logger.exception("❌ Failed to process document '%s': %s", dto.file_path, e)
            raise RuntimeError(f"Document indexing failed: {str(e)}") from e

    # ---------- Overview Query ----------
    def overview_query(self, query_request: DocumentQueryRequest) -> DocumentOverviewResponse:
        """
        Executes a multi-stage overview query on documents.

        Logs query text, top_k value, and number of returned chunks.
        """
        if not self.searcher:
            logger.error("❌ Searcher not initialized.")
            raise RuntimeError("Searcher not initialized.")

        try:
            logger.info("🔍 Overview query started: '%s' (top_k=%d)", query_request.query, query_request.top_k)
            response : DocumentOverviewResponse= self.searcher.overview_query(query_request)
            return response

        except Exception as e:
            logger.exception("❌ Overview query execution failed: %s", e)
            raise RuntimeError(f"Query execution failed: {str(e)}") from e

    # ---------- Chunk Query ----------
    def chunk_query(self, query_request: DocumentQueryRequest) -> DocumentChunkResponse:
        """
        Executes a multi-stage chunk-level query on documents.

        Logs query text, top_k value, and number of returned chunks.
        """
        if not self.searcher:
            logger.error("❌ Searcher not initialized.")
            raise RuntimeError("Searcher not initialized.")

        try:
            logger.info("🔎 Chunk query started: '%s' (top_k=%d)", query_request.query, query_request.top_k)
            response = self.searcher.chunk_query(query_request)
            logger.info("✅ Chunk query completed with %d top chunks.", len(response.top_chunks))
            return response

        except Exception as e:
            logger.exception("❌ Chunk query execution failed: %s", e)
            raise RuntimeError(f"Query execution failed: {str(e)}") from e
