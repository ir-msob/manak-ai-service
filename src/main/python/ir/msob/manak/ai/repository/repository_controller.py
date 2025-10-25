import logging
from fastapi import APIRouter, HTTPException
from src.main.python.ir.msob.manak.ai.repository.model.repository_chunk_response import RepositoryChunkResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_overview_response import RepositoryOverviewResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_request import RepositoryQueryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_request import RepositoryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_response import RepositoryResponse
from src.main.python.ir.msob.manak.ai.repository.repository_service_configuration import RepositoryServiceConfiguration

logger = logging.getLogger(__name__)
router = APIRouter()
service = RepositoryServiceConfiguration.get_repository_service()


@router.get("/", response_model=dict)
def root():
    """Health check endpoint."""
    return {"service": "haystack-milvus-pipeline", "status": "running"}


@router.post("/repository", response_model=RepositoryResponse)
async def add(dto: RepositoryRequest):
    """Indexes a repository."""
    try:
        res: RepositoryResponse = await service.add(dto)
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Error indexing repository from '%s': %s", dto.file_path, e)
        raise HTTPException(status_code=500, detail="Failed to process repository")


@router.post("/repository/overview/query", response_model=RepositoryOverviewResponse)
def overview_query(query_request: RepositoryQueryRequest):
    """Performs overview-level query."""
    if not query_request.query:
        raise HTTPException(status_code=400, detail="Empty query")
    try:
        return service.overview_query(query_request)
    except Exception as e:
        logger.exception("❌ Overview query error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repository/chunk/query", response_model=RepositoryChunkResponse)
def chunk_query(query_request: RepositoryQueryRequest):
    """Performs chunk-level query with summarization."""
    if not query_request.query:
        raise HTTPException(status_code=400, detail="Empty query")
    try:
        return service.chunk_query(query_request)
    except Exception as e:
        logger.exception("❌ Chunk query error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
