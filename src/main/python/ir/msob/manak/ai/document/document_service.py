import asyncio
import logging
from typing import Optional

from src.main.python.ir.msob.manak.ai.client.storage_client import StorageClient
from src.main.python.ir.msob.manak.ai.client.storage_client_configuration import StorageClientConfiguration
from src.main.python.ir.msob.manak.ai.document.model.text_query_request import TextQueryRequest
from src.main.python.ir.msob.manak.ai.document.model.text_query_response import TextQueryResponse
from src.main.python.ir.msob.manak.ai.document.model.document_request import DocumentRequest
from src.main.python.ir.msob.manak.ai.document.document_indexer import DocumentIndexer
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse
from src.main.python.ir.msob.manak.ai.document.document_retriever import MultiStageRetriever

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service responsible for document operations:
    - Downloading and indexing documents
    - Querying and retrieving related information
    """

    def __init__(self):
        self.indexer = DocumentIndexer()
        self.storage_client = StorageClientConfiguration().get_storage_client()
        self.searcher: Optional[MultiStageRetriever] = None

        self._initialize_searcher()

    # ---------- Initialization ----------
    def _initialize_searcher(self):
        """Initialize retriever with safe error handling."""
        try:
            self.searcher = MultiStageRetriever()
            logger.info("✅ MultiStageRetriever initialized successfully.")
        except Exception as e:
            logger.exception("❌ Failed to initialize MultiStageRetriever: %s", e)
            self.searcher = None

    # ---------- Add Document ----------
    async def add(self, dto: DocumentRequest) -> DocumentResponse:
        """
        Downloads a document (from file path or URL) and indexes it.
        """
        logger.info("📥 Starting document addition process for: %s", dto.file_path)

        try:
            # Download file asynchronously
            file_content = await self.storage_client.download_file(dto.file_path)
            logger.info("✅ File downloaded successfully (%d bytes)", len(file_content))

            # Index the content in a background thread to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.indexer.index, dto, file_content)

            logger.info("🧩 Document indexed successfully: %s", result.id)
            return result

        except Exception as e:
            logger.exception("❌ Failed to process document '%s': %s", dto.file_path, e)
            raise RuntimeError(f"Document indexing failed: {str(e)}") from e

    # ---------- Query ----------
    def query_text(self, text_query_request: TextQueryRequest) -> TextQueryResponse:
        """
        Executes a multi-stage search and summarization process based on a text query.
        """
        if not self.searcher:
            logger.error("❌ Searcher not initialized.")
            raise RuntimeError("Searcher not initialized.")

        try:
            logger.info("🔍 Processing text query: '%s' (top_k=%d)",
                        text_query_request.query, text_query_request.top_k)
            response = self.searcher.query_text(text_query_request)
            logger.info("✅ Query completed successfully with %d top chunks.",
                        len(response.top_chunks))
            return response

        except Exception as e:
            logger.exception("❌ Query execution failed: %s", e)
            raise RuntimeError(f"Query execution failed: {str(e)}") from e
