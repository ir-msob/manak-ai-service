import logging
from fastapi import APIRouter, HTTPException

from src.main.python.ir.msob.manak.ai.document.document_service_configuration import DocumentServiceConfiguration
from src.main.python.ir.msob.manak.ai.document.model.document_chunk_response import DocumentChunkResponse
from src.main.python.ir.msob.manak.ai.document.model.document_overview_response import DocumentOverviewResponse
from src.main.python.ir.msob.manak.ai.document.model.document_query_request import DocumentQueryRequest
from src.main.python.ir.msob.manak.ai.document.model.document_request import DocumentRequest
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Documents"])
service = DocumentServiceConfiguration.get_document_service()


def handle_exceptions(func):
    """
    Decorator to catch exceptions and log them before raising HTTPException.
    Supports both async and sync functions.
    """
    import functools
    import inspect
    from fastapi import HTTPException

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.exception("❌ Unexpected error in %s: %s", func.__name__, e)
                raise HTTPException(status_code=500, detail=str(e))

        return wrapper
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.exception("❌ Unexpected error in %s: %s", func.__name__, e)
                raise HTTPException(status_code=500, detail=str(e))

        return wrapper


@router.get("/", response_model=dict, tags=["Health"])
def root():
    """Healthcheck endpoint."""
    logger.info("🚀 Healthcheck requested")
    return {"service": "haystack-milvus-pipeline", "status": "running"}


@router.post("/document", response_model=DocumentResponse, tags=["Documents"])
@handle_exceptions
async def add(dto: DocumentRequest):
    """
    Index a file from URL.

    Logs the incoming request payload for debugging and tracing.
    """
    logger.info("📥 Add document request received: %s", dto.dict())
    return await service.add(dto)


@router.post("/document/overview/query", response_model=DocumentOverviewResponse, tags=["Documents"])
@handle_exceptions
def overview_query(query_request: DocumentQueryRequest):
    """
    Perform an overview query on documents.

    Logs the incoming query for tracing.
    """
    logger.info("🔍 Overview query request received: %s", query_request.dict())
    if not query_request.query:
        raise HTTPException(status_code=400, detail="Empty query")
    return service.overview_query(query_request)


@router.post("/document/chunk/query", response_model=DocumentChunkResponse, tags=["Documents"])
@handle_exceptions
def chunk_query(query_request: DocumentQueryRequest):
    """
    Perform a chunk-level query on documents.

    Logs the incoming query for tracing.
    """
    logger.info("🔎 Chunk query request received: %s", query_request.dict())
    if not query_request.query:
        raise HTTPException(status_code=400, detail="Empty query")
    return service.chunk_query(query_request)
