import logging

from haystack import Pipeline
from haystack.components.writers import DocumentWriter
from milvus_haystack import MilvusDocumentStore, MilvusEmbeddingRetriever
from sentence_transformers import CrossEncoder

from src.main.python.ir.msob.manak.ai.beans.embedder_configuration import EmbedderConfiguration
from src.main.python.ir.msob.manak.ai.config.config import ConfigLoader
from src.main.python.ir.msob.manak.ai.utils.summarizer import ExtractiveSummarizer, AbstractiveSummarizer, \
    HybridSummarizer, HierarchicalSummarizer

logger = logging.getLogger(__name__)
config = ConfigLoader().get_config()


class DocumentChunkConfiguration:
    _document_store: MilvusDocumentStore = None
    _writer: DocumentWriter = None

    _pipeline: Pipeline = None

    _extractive_summarizer: ExtractiveSummarizer = None
    _abstractive_summarizer: AbstractiveSummarizer = None
    _hybrid_summarizer: HybridSummarizer = None
    _hierarchical_summarizer: HierarchicalSummarizer = None

    _cross: CrossEncoder = None

    @classmethod
    def get_store(cls) -> MilvusDocumentStore:
        if cls._document_store is None:
            cls._document_store = MilvusDocumentStore(
                connection_args={"uri": config.milvus.uri},
                collection_name=config.application.milvus.document.chunk.collection_name,
                drop_old=config.application.milvus.document.chunk.drop_old
            )
            logger.info("🔄 Store initialized")
        return cls._document_store

    @classmethod
    def get_writer(cls) -> DocumentWriter:
        if cls._writer is None:
            cls._writer = DocumentWriter(document_store=cls.get_store())
            logger.info("🔄 Writer initialized")
        return cls._writer

    @classmethod
    def get_pipeline(cls) -> Pipeline:
        if cls._pipeline is None:
            pipeline = Pipeline()
            pipeline.add_component("embedder", EmbedderConfiguration.create_embedder())
            pipeline.add_component("writer", cls.get_writer())
            pipeline.connect("embedder.documents", "writer.documents")
            logger.info("🔄 Pipeline initialized")
        return cls._pipeline

    @classmethod
    def get_retriever(cls) -> MilvusEmbeddingRetriever:
        return MilvusEmbeddingRetriever(document_store=cls.get_store())

    @classmethod
    def get_extractive_summarizer(cls) -> ExtractiveSummarizer:
        if cls._extractive_summarizer is None:
            cls._extractive_summarizer = ExtractiveSummarizer(
                model_name=config.application.milvus.document.chunk.extractive_summary.model,
                device=config.application.milvus.document.chunk.extractive_summary.device,
                max_sentences=config.application.milvus.document.chunk.extractive_summary.max_sentences
            )
            logger.info("🔄 ExtractiveSummarizer initialized")
        return cls._extractive_summarizer

    @classmethod
    def get_abstractive_summarizer(cls) -> AbstractiveSummarizer:
        if cls._abstractive_summarizer is None:
            cls._abstractive_summarizer = AbstractiveSummarizer(
                model_name=config.application.milvus.document.chunk.abstractive_summary.model,
                device=config.application.milvus.document.chunk.abstractive_summary.device,
                max_length=config.application.milvus.document.chunk.abstractive_summary.max_length,
                min_length=config.application.milvus.document.chunk.abstractive_summary.min_length
            )
            logger.info("🔄 AbstractiveSummarizer initialized")
        return cls._abstractive_summarizer

    @classmethod
    def get_hybrid_summarizer(cls) -> HybridSummarizer:
        if cls._hybrid_summarizer is None:
            cls._hybrid_summarizer = HybridSummarizer(
                extractive=cls.get_extractive_summarizer(),
                abstractive=cls.get_abstractive_summarizer()
            )
            logger.info("🔄 HybridSummarizer initialized")
        return cls._hybrid_summarizer

    @classmethod
    def get_hierarchical_summarizer(cls) -> HierarchicalSummarizer:
        if cls._hierarchical_summarizer is None:
            cls._hierarchical_summarizer = HierarchicalSummarizer(
                extractive=cls.get_extractive_summarizer(),
                abstractive=cls.get_abstractive_summarizer()
            )
            logger.info("🔄 HierarchicalSummarizer initialized")
        return cls._hierarchical_summarizer

    @classmethod
    def get_cross(cls) -> CrossEncoder:
        if cls._cross is None:
            cls._cross = CrossEncoder(config.application.milvus.cross.model)
            logger.info("🔄 HierarchicalSummarizer initialized")
        return cls._cross
