import logging

from src.main.python.ir.msob.manak.ai.client.rms.rms_client import RmsClient

logger = logging.getLogger(__name__)


class RmsClientConfiguration:
    _rms_client: RmsClient = None

    @classmethod
    def get_rms_client(cls) -> RmsClient:
        if cls._rms_client is None:
            cls._rms_client = RmsClient()
            logger.info("🔄 RmsClient initialized")
        return cls._rms_client
