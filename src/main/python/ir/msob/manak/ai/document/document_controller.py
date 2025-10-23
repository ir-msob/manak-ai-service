import logging

from fastapi import APIRouter, HTTPException

from src.main.python.ir.msob.manak.ai.document.document_service import DocumentService
from src.main.python.ir.msob.manak.ai.document.model.document_request import DocumentRequest
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse
from src.main.python.ir.msob.manak.ai.document.model.text_query_request import TextQueryRequest
from src.main.python.ir.msob.manak.ai.document.model.text_query_response import TextQueryResponse

logger = logging.getLogger(__name__)
router = APIRouter()
service = DocumentService()

@router.get("/", response_model=dict)
def root():
    """Healthcheck endpoint."""
    return {"service": "haystack-milvus-pipeline", "status": "running"}


@router.post(response_model=DocumentResponse)
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


@router.post("/query/text", response_model=TextQueryResponse)
def query_text(text_query_request: TextQueryRequest):
    if not text_query_request.query:
        raise HTTPException(status_code=400, detail="Empty query")
    try:
        result = service.query_text(text_query_request)
        return result
    except Exception as e:
        logger.exception("Error querying text: %s", e)
        raise HTTPException(status_code=500, detail=str(e))