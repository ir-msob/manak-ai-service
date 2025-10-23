import logging
from typing import Any

import aiohttp
from pydantic import ValidationError

from src.main.python.ir.msob.manak.ai.security.keycloak_client_configuration import KeycloakClientConfiguration
from src.main.python.ir.msob.manak.ai.security.model.keycloak_token_response import KeycloakTokenResponse

logger = logging.getLogger(__name__)


class ClientError(Exception):
    """Base custom exception for all service clients."""

    def __init__(self, message: str, *, status: int | None = None, cause: Exception | None = None):
        super().__init__(message)
        self.status = status
        self.cause = cause


class BaseClient:
    """
    🧩 Base asynchronous HTTP client with Keycloak authentication and structured logging.
    Other service clients (e.g., RMS, DMS, etc.) should inherit from this class.
    """

    DEFAULT_TIMEOUT = 30

    def __init__(self, base_url: str, service_name: str, timeout: int | None = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.user_agent = f"{service_name}/1.0"
        self.keycloak_client = KeycloakClientConfiguration.get_keycloak_client()

    # ---------------------------------------------------------------------
    # 🔐 Authentication
    # ---------------------------------------------------------------------
    async def _get_auth_headers(self) -> dict[str, str]:
        """Retrieve a Keycloak access token and build standard headers."""
        try:
            token_response: KeycloakTokenResponse = await self.keycloak_client.get_token()
            return {
                "Authorization": f"Bearer {token_response.access_token}",
                "User-Agent": self.user_agent
            }
        except Exception as ex:
            logger.exception("Failed to obtain Keycloak token")
            raise ClientError("Authentication failed while fetching Keycloak token", cause=ex)

    # ---------------------------------------------------------------------
    # 🌐 Request helpers
    # ---------------------------------------------------------------------
    async def _perform_request(self, url: str, headers: dict[str, str], *, as_bytes: bool = False) -> Any:
        """
        Perform GET request with given headers.
        Returns JSON or bytes depending on `as_bytes`.
        """
        accept_type = "application/octet-stream" if as_bytes else "application/json"
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={**headers, "Accept": accept_type}
            ) as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await (response.read() if as_bytes else response.json())

        except aiohttp.ClientResponseError as cre:
            logger.error(
                f"{self.user_agent} HTTP error",
                extra={"url": url, "status": cre.status, "message": str(cre)}
            )
            raise ClientError(f"HTTP error {cre.status}: {cre.message or str(cre)}", status=cre.status, cause=cre)

        except aiohttp.ClientError as ce:
            logger.error("Network error while contacting service", extra={"url": url, "error": str(ce)})
            raise ClientError(f"Network error: {ce}", cause=ce)

        except Exception as ex:
            logger.exception("Unexpected error during HTTP request", extra={"url": url})
            raise ClientError("Unexpected error during request", cause=ex)

    # ---------------------------------------------------------------------
    # 🧱 Common Model Validation
    # ---------------------------------------------------------------------
    async def _parse_model(self, data: Any, model_cls: type) -> Any:
        """Validate JSON response into a Pydantic model."""
        try:
            return model_cls.model_validate(data)
        except ValidationError as ve:
            logger.error("Invalid response format", extra={"errors": ve.errors()})
            raise ClientError("Invalid response format", cause=ve)
