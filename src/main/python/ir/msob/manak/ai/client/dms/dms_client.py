import logging

from src.main.python.ir.msob.manak.ai.client.base.base_client import BaseClient, ClientError
from src.main.python.ir.msob.manak.ai.client.dms.document_dto import DocumentDto

logger = logging.getLogger(__name__)

class DmsClient(BaseClient):
    def __init__(self, base_url: str | None = None, timeout: int = BaseClient.DEFAULT_TIMEOUT):
        super().__init__(base_url or "http://localhost:8586", "DocumentService", timeout)

    async def get_document(self, doc_id: str) -> DocumentDto:
        logger.info("Fetching document metadata", extra={"doc_id": doc_id})
        url = f"{self.base_url}/api/v1/document/{doc_id}"
        headers = await self._get_auth_headers()
        data = await self._perform_request(url, headers)
        return await self._parse_model(data, DocumentDto)

    async def download_file(self, file_path: str) -> bytes:
        logger.info("Downloading document branch", extra={"file_path": file_path})
        normalized = file_path.lstrip("/")
        url = f"{self.base_url}/api/v1/file/{normalized}"
        headers = await self._get_auth_headers()
        return await self._perform_request(url, headers, as_bytes=True)
