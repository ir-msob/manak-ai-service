import logging

from src.main.python.ir.msob.manak.ai.config.config import ConfigLoader
from src.main.python.ir.msob.manak.ai.config.config_models import RootProperties

logger = logging.getLogger(__name__)


class ConfigConfiguration:
    _properties: RootProperties = None

    @classmethod
    def get_properties(cls) -> RootProperties:
        if cls._properties is None:
            cls._properties = ConfigLoader().get_properties()
            logger.info("🔄 Embedder initialized")
        return cls._properties
