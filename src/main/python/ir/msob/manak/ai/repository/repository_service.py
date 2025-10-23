import logging

from src.main.python.ir.msob.manak.ai.client.rms.repository_dto import RepositoryDto
from src.main.python.ir.msob.manak.ai.client.rms.rms_client_configuration import RmsClientConfiguration
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.document.model.document_query_request import DocumentQueryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_request import RepositoryQueryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_response import RepositoryQueryResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_request import RepositoryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_response import RepositoryResponse
from src.main.python.ir.msob.manak.ai.repository.repository_indexer import RepositoryIndexer
from src.main.python.ir.msob.manak.ai.repository.repository_retriever import RepositoryMultiStageRetriever

logger = logging.getLogger(__name__)
config = ConfigConfiguration().get_properties()


class RepositoryService:
    """
    High-level service used by your API/controllers.
    - add(repository_request): download branch zip, index repository using RepositoryIndexer.
    - query(repository_query_request): delegated to MultiStageRetriever but filters can be applied to restrict to a repo.
    """

    def __init__(self):
        self.rms_client = RmsClientConfiguration().get_rms_client()
        self.indexer = RepositoryIndexer()
        self.searcher = RepositoryMultiStageRetriever()


    async def add(self, dto: RepositoryRequest) -> RepositoryResponse:
        """
        dto should contain repository_id and optionally branch.
        Behavior:
          - download branch (zip) via rms client
          - index with RepositoryIndexer
          - return RepositoryResponse (contains indexed_files list and overview id)
        """
        logger.info("Repository add requested: %s", getattr(dto, "repository_id", "<none>"))

        try:
            repository: RepositoryDto = await self.rms_client.get_repository(dto.repository_id)
            branch = dto.branch

            # download zip; adapt call if your client requires branch param
            if branch:
                zip_bytes = await self.rms_client.download_branch(dto.repository_id, branch)
            else:
                zip_bytes = await self.rms_client.download_branch(dto.repository_id)

            result = self.indexer.index_repository(repository, branch, zip_bytes)

            # build RepositoryResponse — adapt fields to your actual model if necessary
            resp = RepositoryResponse(**{
                "id": result["repository_id"],
                "name": result.get("name"),
                "indexed_files": result.get("indexed_files"),
                "overview_id": result.get("overview_id"),
                "branch": branch
            })

            logger.info("Repository indexed successfully: %s", repository.id)
            return resp

        except Exception as e:
            logger.exception("Failed to add/index repository %s: %s", getattr(dto, "repository_id", "<unknown>"), e)
            raise RuntimeError(f"Repository add failed: {e}") from e

    def query(self, query_request: RepositoryQueryRequest) -> RepositoryQueryResponse:
        """
        Query across indexed repository data.
        By default calls MultiStageRetriever; if query_request includes repository_id, we add a filter to retriever(s).
        """
        if not self.searcher:
            logger.error("Searcher not available for repository query.")
            raise RuntimeError("Searcher not initialized")

        try:

            # if repository filter present, set filters on the retrievers
            repo_id = getattr(query_request, "repository_id", None)
            if repo_id:
                # apply filter on overview and chunk retrievers so results limited to that repo
                # Structure used earlier in code: {"operator":"AND","conditions":[...]}
                # We'll set filters directly on retriever instances
                overview_retriever = self.searcher.overview_retriever
                chunk_retriever = self.searcher.chunk_retriever
                overview_retriever.filters = {"operator": "AND", "conditions": [
                    {"field": "repository_id", "operator": "in", "value": [repo_id]}]}
                chunk_retriever.filters = {"operator": "AND", "conditions": [
                    {"field": "repository_id", "operator": "in", "value": [repo_id]}]}

            response = self.searcher.query(query_request)

            # map to RepositoryQueryResponse — adapt to your actual model
            return response

        except Exception as e:
            logger.exception("Repository query failed: %s", e)
            raise RuntimeError(f"Repository query failed: {e}") from e
