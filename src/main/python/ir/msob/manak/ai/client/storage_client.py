import logging

import aiohttp

from src.main.python.ir.msob.manak.ai.security.keycloak_client_configuration import KeycloakClientConfiguration
from src.main.python.ir.msob.manak.ai.security.model.keycloak_token_response import KeycloakTokenResponse

logger = logging.getLogger(__name__)


class StorageClient:
    """Handles file download operations from storage service with Keycloak authentication."""

    def __init__(self):
        self.storage_service_base_url = "http://storage/api/v1/storage"
        self.timeout = 30
        self.keycloak_client = KeycloakClientConfiguration.get_keycloak_client()

    async def download_file(self, file_path: str) -> bytes:
        """
        Download file content from storage service using Keycloak token.

        Args:
            file_path: Path to the file in storage service

        Returns:
            file_content
        """
        try:
            # Get Keycloak token
            token_response: KeycloakTokenResponse = await self.keycloak_client.get_token()
            auth_header = {"Authorization": f"Bearer {token_response.access_token}"}

            # Construct the full URL for storage service
            download_url = f"{self.storage_service_base_url}/file/{file_path.lstrip('/')}"

            logger.info("Downloading file from storage service: %s", download_url)

            async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={**auth_header, "User-Agent": "DocumentService/1.0", "Accept": "application/octet-stream"}
            ) as session:
                async with session.get(download_url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    logger.info("Successfully downloaded file '%s' (%d bytes) from storage service",
                                file_path, len(content))
                    return content

        except aiohttp.ClientError as e:
            logger.error("Error downloading file from storage service '%s': %s", file_path, e)
            raise Exception(f"Failed to download file from storage service: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error downloading file from storage service '%s': %s", file_path, e)
            raise
