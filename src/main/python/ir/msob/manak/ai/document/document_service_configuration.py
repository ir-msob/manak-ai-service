import logging

from src.main.python.ir.msob.manak.ai.document.document_service import DocumentService

logger = logging.getLogger(__name__)

class DocumentServiceConfiguration:
    _document_service: DocumentService = None

    @classmethod
    def get_document_service(cls) -> DocumentService:
        if cls._document_service is None:
            cls._document_service = DocumentService()
            logger.info("🔄 DocumentService initialized")
        return cls._document_service
