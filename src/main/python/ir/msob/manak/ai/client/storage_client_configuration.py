import logging

from src.main.python.ir.msob.manak.ai.client.storage_client import StorageClient
from src.main.python.ir.msob.manak.ai.config.config import ConfigLoader

logger = logging.getLogger(__name__)
config = ConfigLoader().get_config()


class StorageClientConfiguration:
    _storage_client: StorageClient = None

    @classmethod
    def get_storage_client(cls) -> StorageClient:
        if cls._storage_client is None:
            cls._storage_client = StorageClient()
            logger.info("🔄 StorageClient initialized")
        return cls._storage_client
