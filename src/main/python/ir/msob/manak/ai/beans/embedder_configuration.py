import logging

from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.utils import ComponentDevice

from src.main.python.ir.msob.manak.ai.config.config import ConfigLoader

logger = logging.getLogger(__name__)
config = ConfigLoader().get_config()


class EmbedderConfiguration:
    _embedder: SentenceTransformersDocumentEmbedder = None

    @classmethod
    def get_embedder(cls) -> SentenceTransformersDocumentEmbedder:
        if cls._embedder is None:
            cls._embedder = cls.create_embedder()
            logger.info("🔄 Embedder initialized")
        return cls._embedder

    @classmethod
    def create_embedder(cls) -> SentenceTransformersDocumentEmbedder:
        embedder = SentenceTransformersDocumentEmbedder(
            model=config.application.milvus.embedding.model,
            device=ComponentDevice.from_str(config.application.milvus.embedding.device)
        )
        embedder.warm_up()
        return embedder
