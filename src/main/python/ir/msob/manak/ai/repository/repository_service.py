import logging
import time
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

    # ------------------------------------------------------------------------------------
    async def add(self, dto: RepositoryRequest) -> RepositoryResponse:
        """
        Indexes a repository by downloading its branch and processing it.
        """
        start_time = time.time()
        logger.info("➡️ [RepositoryService.add] Start indexing | repo_id=%s | branch=%s",
                    dto.repository_id, getattr(dto, "branch", None))
        try:
            # Step 1: Fetch repository metadata
            repository: RepositoryDto = await self.rms_client.get_repository(dto.repository_id)
            branch = dto.branch
            logger.debug("📦 Repository metadata loaded | name=%s | branches=%s",
                         repository.name, getattr(repository, "branches", []))

            # Step 2: Download zip content
            logger.info("⬇️ Downloading branch '%s' for repository '%s'...", branch, dto.repository_id)
            zip_bytes = await self.rms_client.download_branch(dto.repository_id, branch) if branch \
                else await self.rms_client.download_branch(dto.repository_id)
            logger.debug("📁 Repository ZIP downloaded | size=%d bytes", len(zip_bytes))

            # Step 3: Index repository
            logger.info("⚙️ Indexing repository content for '%s'...", repository.name)
            result = self.indexer.index(repository, branch, zip_bytes)
            logger.debug("🧩 Index result keys: %s", list(result.keys()))

            # Step 4: Build response
            resp = RepositoryResponse(
                repository_id=repository.id,
                name=repository.name,
                branch=branch,
                indexed_files=result.get("indexed_files"),
                overview_id=result.get("overview_id"),
            )

            duration = round(time.time() - start_time, 2)
            logger.info("✅ Repository indexed successfully | repo_id=%s | files=%d | duration=%.2fs",
                        repository.id,
                        len(result.get("indexed_files", [])) if result.get("indexed_files") else 0,
                        duration)
            return resp

        except Exception as e:
            logger.exception("❌ Failed to index repository '%s': %s", getattr(dto, "repository_id", "<unknown>"), e)
            raise RuntimeError(f"Repository add failed: {e}") from e

    # ------------------------------------------------------------------------------------
    def overview_query(self, query_request: RepositoryQueryRequest) -> RepositoryOverviewResponse:
        """
        Performs an overview-level semantic search.
        """
        start_time = time.time()
        logger.info("➡️ [RepositoryService.overview_query] Start overview query | query='%s' | top_k=%d | repos=%s",
                    query_request.query, query_request.top_k, query_request.repository_ids)
        try:
            response = self.searcher.overview_query(query_request)
            result_count = len(response.overviews) if response and response.overviews else 0
            duration = round(time.time() - start_time, 2)
            logger.info("✅ Overview query completed | results=%d | duration=%.2fs", result_count, duration)
            logger.debug("🔍 Overview query details: first result=%s",
                         response.overviews[0].repository_id if result_count > 0 else "None")
            return response
        except Exception as e:
            logger.exception("❌ Overview query failed for '%s': %s", query_request.query, e)
            raise RuntimeError(f"Overview query failed: {e}") from e

    # ------------------------------------------------------------------------------------
    def chunk_query(self, query_request: RepositoryQueryRequest) -> RepositoryChunkResponse:
        """
        Performs a chunk-level semantic search and generates a summary.
        """
        start_time = time.time()
        logger.info("➡️ [RepositoryService.chunk_query] Start chunk query | query='%s' | top_k=%d | repos=%s",
                    query_request.query, query_request.top_k, query_request.repository_ids)
        try:
            response = self.searcher.chunk_query(query_request)
            chunk_count = len(response.top_chunks) if response and response.top_chunks else 0
            duration = round(time.time() - start_time, 2)

            logger.info("✅ Chunk query completed | chunks=%d | duration=%.2fs", chunk_count, duration)
            if response.final_summary:
                logger.debug("🧠 Summary preview: %s", response.final_summary[:150])
            return response

        except Exception as e:
            logger.exception("❌ Chunk query failed for '%s': %s", query_request.query, e)
            raise RuntimeError(f"Chunk query failed: {e}") from e
