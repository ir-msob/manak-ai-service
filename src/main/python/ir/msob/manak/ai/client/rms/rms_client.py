import logging

from src.main.python.ir.msob.manak.ai.client.base.base_client import BaseClient, ClientError
from src.main.python.ir.msob.manak.ai.client.rms.repository_dto import RepositoryDto

logger = logging.getLogger(__name__)


class RmsClient(BaseClient):
    def __init__(self, base_url: str | None = None, timeout: int = BaseClient.DEFAULT_TIMEOUT):
        super().__init__(base_url or "http://localhost:8587", "RepositoryService", timeout)

    async def get_repository(self, repo_id: str) -> RepositoryDto:
        url = f"{self.base_url}/api/v1/repository/{repo_id}"
        logger.info("Fetching repository metadata", extra={"repo_id": repo_id})
        headers = await self._get_auth_headers()
        data = await self._perform_request(url, headers)
        return await self._parse_model(data, RepositoryDto)

    async def download_branch(self, repo_id: str) -> bytes:
        url = f"{self.base_url}/api/v1/repository/{repo_id}/download"
        logger.info("Downloading repository branch", extra={"repo_id": repo_id})
        headers = await self._get_auth_headers()
        return await self._perform_request(url, headers, as_bytes=True)

    async def download_branch(self, repo_id: str, branch: str) -> bytes:
        url = f"{self.base_url}/api/v1/repository/{repo_id}/branch/{branch}/download"
        logger.info("Downloading repository branch", extra={"repo_id": repo_id})
        headers = await self._get_auth_headers()
        return await self._perform_request(url, headers, as_bytes=True)
