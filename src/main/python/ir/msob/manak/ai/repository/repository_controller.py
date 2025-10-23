import logging

from fastapi import APIRouter, HTTPException

from src.main.python.ir.msob.manak.ai.repository.model.repository_query_request import RepositoryQueryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_response import RepositoryQueryResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_request import RepositoryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_response import RepositoryResponse
from src.main.python.ir.msob.manak.ai.repository.repository_service_configuration import RepositoryServiceConfiguration

logger = logging.getLogger(__name__)
router = APIRouter()
service = RepositoryServiceConfiguration.get_repository_service()

@router.get("/", response_model=dict)
def root():
    """Healthcheck endpoint."""
    return {"service": "haystack-milvus-pipeline", "status": "running"}


@router.post(response_model=RepositoryResponse)
async def add(dto: RepositoryRequest):
    """Index a file from URL."""
    try:

        # Delegate to service layer
        res: RepositoryResponse = await service.add(dto)
        return res

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error processing file from '%s': %s", dto.file_path, e)
        raise HTTPException(status_code=500, detail="Failed to process file")


@router.post("/query", response_model=RepositoryQueryResponse)
def query(query_request: RepositoryQueryRequest):
    if not query_request.query:
        raise HTTPException(status_code=400, detail="Empty query")
    try:
        result = service.query(query_request)
        return result
    except Exception as e:
        logger.exception("Error querying text: %s", e)
        raise HTTPException(status_code=500, detail=str(e))