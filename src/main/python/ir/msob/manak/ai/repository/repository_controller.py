import logging
from fastapi import APIRouter, HTTPException, Request
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
async def root(request: Request):
    """Health check endpoint."""
    logger.info("➡️ [GET %s] Health check called from %s", request.url.path, request.client.host)
    return {"service": "haystack-milvus-pipeline", "status": "running"}


@router.post("/repository", response_model=RepositoryResponse)
async def add(request: Request, dto: RepositoryRequest):
    """Indexes a repository."""
    logger.info(
        "➡️ [POST %s] Received repository indexing request from %s | repo_id=%s | branch=%s",
        request.url.path,
        request.client.host,
        dto.repository_id,
        dto.branch
    )
    try:
        res: RepositoryResponse = await service.add(dto)
        logger.info("✅ Successfully indexed repository '%s' on branch '%s'", dto.repository_id, dto.branch)
        return res

    except HTTPException as e:
        logger.warning("⚠️ HTTPException while indexing repository '%s': %s", dto.repository_id, e.detail)
        raise

    except Exception as e:
        logger.exception("❌ Unexpected error while indexing repository '%s': %s", dto.repository_id, e)
        raise HTTPException(status_code=500, detail="Failed to process repository")


@router.post("/repository/overview/query", response_model=RepositoryOverviewResponse)
async def overview_query(request: Request, query_request: RepositoryQueryRequest):
    """Performs overview-level query."""
    logger.info(
        "➡️ [POST %s] Overview query request from %s | query='%s' | top_k=%d | repos=%s",
        request.url.path,
        request.client.host,
        query_request.query,
        query_request.top_k,
        query_request.repository_ids
    )

    if not query_request.query:
        logger.warning("⚠️ Received empty query for overview search.")
        raise HTTPException(status_code=400, detail="Empty query")

    try:
        result = service.overview_query(query_request)
        logger.info(
            "✅ Overview query for '%s' returned %d results",
            query_request.query,
            len(result.overviews) if result and result.overviews else 0
        )
        return result

    except Exception as e:
        logger.exception("❌ Overview query error for query='%s': %s", query_request.query, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repository/chunk/query", response_model=RepositoryChunkResponse)
async def chunk_query(request: Request, query_request: RepositoryQueryRequest):
    """Performs chunk-level query with summarization."""
    logger.info(
        "➡️ [POST %s] Chunk query request from %s | query='%s' | top_k=%d | repos=%s",
        request.url.path,
        request.client.host,
        query_request.query,
        query_request.top_k,
        query_request.repository_ids
    )

    if not query_request.query:
        logger.warning("⚠️ Received empty query for chunk search.")
        raise HTTPException(status_code=400, detail="Empty query")

    try:
        result = service.chunk_query(query_request)
        logger.info(
            "✅ Chunk query for '%s' returned %d chunks",
            query_request.query,
            len(result.top_chunks) if result and result.top_chunks else 0
        )
        if result.final_summary:
            logger.debug("🧠 Summary (first 100 chars): %s", result.final_summary[:100])
        return result

    except Exception as e:
        logger.exception("❌ Chunk query error for query='%s': %s", query_request.query, e)
        raise HTTPException(status_code=500, detail=str(e))
