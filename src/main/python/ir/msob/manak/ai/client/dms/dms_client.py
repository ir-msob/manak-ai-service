import logging
from typing import Any

import aiohttp
from pydantic import ValidationError

from src.main.python.ir.msob.manak.ai.client.dms.document_dto import DocumentDto
from src.main.python.ir.msob.manak.ai.security.keycloak_client_configuration import KeycloakClientConfiguration
from src.main.python.ir.msob.manak.ai.security.model.keycloak_token_response import KeycloakTokenResponse

logger = logging.getLogger(__name__)


class DmsClient:
    """Reactive-style async client for communicating with DMS (Document Management Service)."""

    DEFAULT_TIMEOUT = 30
    USER_AGENT = "DocumentService/1.0"

    def __init__(self, base_url: str | None = None, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url or "http://localhost:8586"
        self.timeout = timeout
        self.keycloak_client = KeycloakClientConfiguration.get_keycloak_client()

    # -----------------------------
    # 🔑 Helper Methods
    # -----------------------------
    async def _get_auth_headers(self) -> dict[str, str]:
        """Retrieve Keycloak token and return authorization headers."""
        token_response: KeycloakTokenResponse = await self.keycloak_client.get_token()
        return {
            "Authorization": f"Bearer {token_response.access_token}",
            "User-Agent": self.USER_AGENT
        }

    async def _request_json(self, url: str, headers: dict[str, str]) -> Any:
        """Perform a GET request expecting JSON response."""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={**headers, "Accept": "application/json"}
        ) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def _request_bytes(self, url: str, headers: dict[str, str]) -> bytes:
        """Perform a GET request expecting binary response."""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={**headers, "Accept": "application/octet-stream"}
        ) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()

    # -----------------------------
    # 📄 Public Methods
    # -----------------------------
    async def get_document(self, document_id: str) -> DocumentDto:
        """
        Retrieve document metadata from DMS and parse it into a DocumentDto.
        """
        url = f"{self.base_url}/api/v1/document/{document_id}"
        logger.info("Fetching document metadata", extra={"url": url, "document_id": document_id})

        try:
            headers = await self._get_auth_headers()
            data = await self._request_json(url, headers)
            logger.debug("Document metadata JSON received", extra={"document_id": document_id, "keys": list(data.keys())})

            return DocumentDto.model_validate(data)

        except ValidationError as ve:
            logger.error("Invalid document data format", extra={"document_id": document_id, "errors": ve.errors()})
            raise
        except aiohttp.ClientResponseError as cre:
            logger.error("DMS responded with HTTP error",
                         extra={"document_id": document_id, "status": cre.status, "message": str(cre)})
            raise Exception(f"DMS HTTP error ({cre.status}): {cre.message or str(cre)}") from cre
        except aiohttp.ClientError as ce:
            logger.error("Network or client error while fetching document",
                         extra={"document_id": document_id, "error": str(ce)})
            raise Exception(f"Network error fetching document: {ce}") from ce
        except Exception:
            logger.exception("Unexpected error while fetching document", extra={"document_id": document_id})
            raise

    async def download_file(self, file_path: str) -> bytes:
        """
        Download a file from DMS using secure Keycloak token authentication.
        """
        normalized_path = file_path.lstrip("/")
        download_url = f"{self.base_url}/api/v1/file/{normalized_path}"
        logger.info("Downloading file", extra={"path": normalized_path, "url": download_url})

        try:
            headers = await self._get_auth_headers()
            content = await self._request_bytes(download_url, headers)

            logger.info("File downloaded successfully",
                        extra={"path": normalized_path, "size_bytes": len(content)})
            return content

        except aiohttp.ClientResponseError as cre:
            logger.error("DMS returned HTTP error while downloading file",
                         extra={"path": file_path, "status": cre.status, "message": str(cre)})
            raise Exception(f"DMS HTTP error ({cre.status}) while downloading file: {cre.message or str(cre)}") from cre
        except aiohttp.ClientError as ce:
            logger.error("Network or client error while downloading file",
                         extra={"path": file_path, "error": str(ce)})
            raise Exception(f"Network error downloading file: {ce}") from ce
        except Exception:
            logger.exception("Unexpected error while downloading file", extra={"path": file_path})
            raise
