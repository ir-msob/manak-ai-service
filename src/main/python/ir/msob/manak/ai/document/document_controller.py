import logging

from fastapi import APIRouter, HTTPException

from src.main.python.ir.msob.manak.ai.document.document_service import DocumentService
from src.main.python.ir.msob.manak.ai.document.document_service_configuration import DocumentServiceConfiguration
from src.main.python.ir.msob.manak.ai.document.model.document_request import DocumentRequest
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse
from src.main.python.ir.msob.manak.ai.document.model.document_query_request import DocumentQueryRequest
from src.main.python.ir.msob.manak.ai.document.model.document_query_response import DocumentQueryResponse

logger = logging.getLogger(__name__)
router = APIRouter()
service = DocumentServiceConfiguration.get_document_service()

@router.get("/", response_model=dict)
def root():
    """Healthcheck endpoint."""
    return {"service": "haystack-milvus-pipeline", "status": "running"}


@router.post(path="/document", response_model=DocumentResponse)
async def add(dto: DocumentRequest):
    """Index a file from URL."""
    try:

        # Delegate to service layer
        res: DocumentResponse = await service.add(dto)
        return res

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error processing file from '%s': %s", dto.file_path, e)
        raise HTTPException(status_code=500, detail="Failed to process file")


@router.post("/document/query", response_model=DocumentQueryResponse)
def query(query_request: DocumentQueryRequest):
    if not query_request.query:
        raise HTTPException(status_code=400, detail="Empty query")
    try:
        result = service.query(query_request)
        return result
    except Exception as e:
        logger.exception("Error querying text: %s", e)
        raise HTTPException(status_code=500, detail=str(e))