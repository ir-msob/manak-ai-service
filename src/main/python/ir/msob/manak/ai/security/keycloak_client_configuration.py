import logging

from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.security.keycloak_client import KeycloakClient

logger = logging.getLogger(__name__)
config = ConfigConfiguration().get_properties()


class KeycloakClientConfiguration:
    _keycloak_client: KeycloakClient = None

    @classmethod
    def get_keycloak_client(cls) -> KeycloakClient:
        if cls._keycloak_client is None:
            cls._keycloak_client = KeycloakClient()
            logger.info("🔄 KeycloakClient initialized")
        return cls._keycloak_client
