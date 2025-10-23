import logging

from src.main.python.ir.msob.manak.ai.client.dms.dms_client import DmsClient
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration

logger = logging.getLogger(__name__)
config = ConfigConfiguration().get_properties()


class DmsClientConfiguration:
    _dms_client: DmsClient = None

    @classmethod
    def get_dms_client(cls) -> DmsClient:
        if cls._dms_client is None:
            cls._dms_client = DmsClient()
            logger.info("🔄 DmsClient initialized")
        return cls._dms_client
