import logging

from src.main.python.ir.msob.manak.ai.repository.repository_service import RepositoryService

logger = logging.getLogger(__name__)


class RepositoryServiceConfiguration:
    _repository_service: RepositoryService = None

    @classmethod
    def get_repository_service(cls) -> RepositoryService:
        if cls._repository_service is None:
            cls._repository_service = RepositoryService()
            logger.info("🔄 RepositoryService initialized")
        return cls._repository_service
