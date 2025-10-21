import logging

from src.main.python.ir.msob.manak.ai.client.storage_client import StorageClient
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration

logger = logging.getLogger(__name__)
config = ConfigConfiguration().get_properties()


class StorageClientConfiguration:
    _storage_client: StorageClient = None

    @classmethod
    def get_storage_client(cls) -> StorageClient:
        if cls._storage_client is None:
            cls._storage_client = StorageClient()
            logger.info("🔄 StorageClient initialized")
        return cls._storage_client
