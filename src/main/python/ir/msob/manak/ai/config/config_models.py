# src/main/python/ir/msob/manak/ai/config/config_models.py
from typing import Optional, Dict, Any

from pydantic import BaseModel


# ===============================
# Basic Sections
# ===============================
class ServerProperties(BaseModel):
    port: int


class PythonApplicationProperties(BaseModel):
    name: str


# ===============================
# Security Section
# ===============================
class JwtProperties(BaseModel):
    issuer_uri: str


class ResourceServerProperties(BaseModel):
    jwt: JwtProperties


class OAuth2ClientRegistrationProperties(BaseModel):
    client_name: str
    client_id: str
    client_secret: str
    authorization_grant_type: str
    client_authentication_method: str
    scope: list[str]

class OAuth2ClientProperties(BaseModel):
    provider: Dict[str, Dict[str, str]]
    registration: Dict[str, OAuth2ClientRegistrationProperties]

class OAuth2Properties(BaseModel):
    resource_server: ResourceServerProperties
    client: OAuth2ClientProperties


class SecurityProperties(BaseModel):
    oauth2: OAuth2Properties


class PythonProperties(BaseModel):
    application: PythonApplicationProperties
    profiles: Dict[str, str]
    security: Optional[SecurityProperties] = None


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


class ApplicationProperties(BaseModel):
    milvus: MilvusApplicationProperties


# ===============================
# Root Config
# ===============================
class RootProperties(BaseModel):
    server: ServerProperties
    python: PythonProperties
    milvus: MilvusProperties
    models: ModelsProperties
    application: ApplicationProperties
