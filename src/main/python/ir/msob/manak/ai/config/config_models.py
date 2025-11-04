import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


# ===============================
# Eureka Section
# ===============================
class EurekaClientProperties(BaseModel):
    service_url: Dict[str, str]


class EurekaInstanceProperties(BaseModel):
    appname: str
    instance_id: str
    prefer_ip_address: bool


class EurekaProperties(BaseModel):
    client: EurekaClientProperties
    instance: EurekaInstanceProperties


# ===============================
# Basic Sections
# ===============================
class ServerProperties(BaseModel):
    port: int


class PythonApplicationProperties(BaseModel):
    name: str
    base_url: Optional[str] = None


# ===============================
# Security Section
# ===============================
class JwtProperties(BaseModel):
    issuer_uri: str


class ResourceServerProperties(BaseModel):
    jwt: JwtProperties


class OAuth2ProviderProperties(BaseModel):
    issuer_uri: str


class OAuth2ClientProviderProperties(BaseModel):
    service_client: OAuth2ProviderProperties


class OAuth2ClientRegistrationProperties(BaseModel):
    client_name: str
    client_id: str
    client_secret: str
    authorization_grant_type: str
    client_authentication_method: str
    scope: List[str]


class OAuth2ClientRegistrationMap(BaseModel):
    service_client: OAuth2ClientRegistrationProperties


class OAuth2ClientProperties(BaseModel):
    provider: OAuth2ClientProviderProperties
    registration: OAuth2ClientRegistrationMap


class OAuth2Properties(BaseModel):
    resource_server: ResourceServerProperties
    client: OAuth2ClientProperties


class SecurityProperties(BaseModel):
    oauth2: OAuth2Properties


# ===============================
# Python Section
# ===============================
class PythonProfilesProperties(BaseModel):
    active: List[str]


class PythonProperties(BaseModel):
    application: PythonApplicationProperties
    profiles: PythonProfilesProperties
    security: Optional[SecurityProperties] = None
    eureka: Optional[EurekaProperties] = None


# ===============================
# Kafka Section
# ===============================
class KafkaConsumerProperties(BaseModel):
    group_id: str
    key_deserializer: str
    value_deserializer: str
    bootstrap_servers: str


class KafkaProducerProperties(BaseModel):
    key_serializer: str
    value_serializer: str
    bootstrap_servers: str


class KafkaProperties(BaseModel):
    bootstrap_servers: str
    consumer: Optional[KafkaConsumerProperties] = None
    producer: Optional[KafkaProducerProperties] = None


# ===============================
# Tool Section
# ===============================
class ToolProperties(BaseModel):
    tool_provider_topic: str


# ===============================
# Model Paths Section
# ===============================
class ModelsProperties(BaseModel):
    embedding_model: str
    summarization_model: str
    reranker_model: str
    cross_model: Optional[str] = None


# ===============================
# Milvus Section
# ===============================
class MilvusProperties(BaseModel):
    uri: str


# ===============================
# Index / Retriever / Model Sections
# ===============================
class IndexProperties(BaseModel):
    type: str
    params: Dict[str, Any]
    metric_type: str


class RetrieverProperties(BaseModel):
    top_k: Optional[int] = None
    rerank_top_k: Optional[int] = None
    final_summary_extract_k: Optional[int] = None


class EmbeddingProperties(BaseModel):
    model: str
    device: str


class CrossProperties(BaseModel):
    model: str


class SummaryProperties(BaseModel):
    model: str
    device: str
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    max_sentences: Optional[int] = None


class RerankerProperties(BaseModel):
    model: str
    device: str


# ===============================
# Document / Repository Sections
# ===============================
class OverviewProperties(BaseModel):
    collection_name: str
    index: IndexProperties
    drop_old: bool
    extract_k_per_chunk: Optional[int] = None
    retriever: RetrieverProperties
    abstractive_summary: Optional[SummaryProperties] = None
    extractive_summary: Optional[SummaryProperties] = None


class ChunkProperties(BaseModel):
    collection_name: str
    index: IndexProperties
    drop_old: bool
    chunk_words_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    retriever: RetrieverProperties
    reranker: Optional[RerankerProperties] = None
    abstractive_summary: Optional[SummaryProperties] = None
    extractive_summary: Optional[SummaryProperties] = None


class MilvusDocumentProperties(BaseModel):
    overview: OverviewProperties
    chunk: ChunkProperties


class MilvusRepositoryProperties(BaseModel):
    overview: OverviewProperties
    chunk: ChunkProperties


class MilvusApplicationProperties(BaseModel):
    embedding: EmbeddingProperties
    cross: CrossProperties
    document: MilvusDocumentProperties
    repository: MilvusRepositoryProperties


# ===============================
# Application Section
# ===============================
class ApplicationProperties(BaseModel):
    milvus: MilvusApplicationProperties


# ===============================
# Root Config
# ===============================
class RootProperties(BaseModel):
    server: ServerProperties
    python: PythonProperties
    milvus: MilvusProperties
    kafka: Optional[KafkaProperties] = None
    tool: Optional[ToolProperties] = None
    models: ModelsProperties
    application: ApplicationProperties