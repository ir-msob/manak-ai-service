import logging

import aiohttp

from src.main.python.ir.msob.manak.ai.config.config import ConfigLoader
from src.main.python.ir.msob.manak.ai.security.model.keycloak_token_request import KeycloakTokenRequest
from src.main.python.ir.msob.manak.ai.security.model.keycloak_token_response import KeycloakTokenResponse

logger = logging.getLogger(__name__)
config = ConfigLoader().get_config()


class KeycloakClient:
    def __init__(self):
        self.token_url = f"{config.python.security.oauth2.resource_server.jwt.issuer_uri}/protocol/openid-connect/token"

    async def get_token(self) -> KeycloakTokenResponse:
        client_conf = config.python.security.oauth2.client.registration.get("service_client")

        logger.info("Requesting new Keycloak token for client '%s'", client_conf.client_id)

        # ساخت مدل request
        request_payload = KeycloakTokenRequest(
            grant_type=client_conf.authorization_grant_type,
            client_id=client_conf.client_id,
            client_secret=client_conf.client_secret
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=request_payload.to_dict()) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise Exception(f"Failed to obtain Keycloak token: {resp.status} {body}")

                token_data = await resp.json()
                return KeycloakTokenResponse(**token_data)

