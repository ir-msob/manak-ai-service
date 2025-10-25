import logging

from src.main.python.ir.msob.manak.ai.client.rms.repository_dto import RepositoryDto
from src.main.python.ir.msob.manak.ai.client.rms.rms_client_configuration import RmsClientConfiguration
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.repository.model.repository_chunk_response import RepositoryChunkResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_overview_response import RepositoryOverviewResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_request import RepositoryQueryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_request import RepositoryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_response import RepositoryResponse
from src.main.python.ir.msob.manak.ai.repository.repository_indexer import RepositoryIndexer
from src.main.python.ir.msob.manak.ai.repository.repository_retriever import RepositoryMultiStageRetriever

logger = logging.getLogger(__name__)
config = ConfigConfiguration().get_properties()


class RepositoryService:
    """
    High-level service responsible for:
      - Indexing repositories
      - Performing overview & chunk queries
    """

    def __init__(self):
        self.rms_client = RmsClientConfiguration().get_rms_client()
        self.indexer = RepositoryIndexer()
        self.searcher = RepositoryMultiStageRetriever()

    async def add(self, dto: RepositoryRequest) -> RepositoryResponse:
        """
        Indexes a repository by downloading its branch and processing it.
        """
        logger.info("📦 Indexing repository: %s (branch=%s)", dto.repository_id, getattr(dto, "branch", None))
        try:
            repository: RepositoryDto = await self.rms_client.get_repository(dto.repository_id)
            branch = dto.branch

            # Download zip file
            zip_bytes = await self.rms_client.download_branch(dto.repository_id, branch) if branch \
                else await self.rms_client.download_branch(dto.repository_id)

            # Index repository contents
            result = self.indexer.index(repository, branch, zip_bytes)

            # Build response
            resp = RepositoryResponse(
                repository_id=repository.id,
                name=repository.name,
                branch=branch,
                indexed_files=result.get("indexed_files"),
                overview_id=result.get("overview_id"),
            )

            logger.info("✅ Repository indexed successfully: %s", repository.id)
            return resp

        except Exception as e:
            logger.exception("❌ Failed to index repository %s: %s", getattr(dto, "repository_id", "<unknown>"), e)
            raise RuntimeError(f"Repository add failed: {e}") from e

    def overview_query(self, query_request: RepositoryQueryRequest) -> RepositoryOverviewResponse:
        """
        Performs an overview-level semantic search.
        """
        logger.info("🔍 Starting overview query for: '%s'", query_request.query)
        try:
            response = self.searcher.overview_query(query_request)
            logger.info("✅ Overview query completed successfully.")
            return response
        except Exception as e:
            logger.exception("❌ Overview query failed: %s", e)
            raise RuntimeError(f"Overview query failed: {e}") from e

    def chunk_query(self, query_request: RepositoryQueryRequest) -> RepositoryChunkResponse:
        """
        Performs a chunk-level semantic search and generates a summary.
        """
        logger.info("🔍 Starting chunk query for: '%s'", query_request.query)
        try:
            response = self.searcher.chunk_query(query_request)
            logger.info("✅ Chunk query completed successfully.")
            return response
        except Exception as e:
            logger.exception("❌ Chunk query failed: %s", e)
            raise RuntimeError(f"Chunk query failed: {e}") from e
