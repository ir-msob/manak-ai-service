import logging

from src.main.python.ir.msob.manak.ai.client.dms.dms_client import DmsClient

logger = logging.getLogger(__name__)

class DmsClientConfiguration:
    _dms_client: DmsClient = None

    @classmethod
    def get_dms_client(cls) -> DmsClient:
        if cls._dms_client is None:
            cls._dms_client = DmsClient()
            logger.info("🔄 DmsClient initialized")
        return cls._dms_client
