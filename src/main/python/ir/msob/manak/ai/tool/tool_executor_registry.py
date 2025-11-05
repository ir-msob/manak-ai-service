import logging
from typing import Callable, Any, Optional
from src.main.python.ir.msob.manak.ai.tool.model.invoke_request import InvokeRequest

logger = logging.getLogger(__name__)


# ---------------------- Tool Registry ----------------------
class ToolExecutorRegistry:
    """Registry for dynamic tools."""

    def __init__(self):
        self._registry: dict[str, Callable[[Any, InvokeRequest], Any]] = {}

    def register(self, tool_id: str):
        """Decorator to register a tool handler."""

        def decorator(func: Callable[[Any, InvokeRequest], Any]):
            self._registry[tool_id] = func
            logger.info(f"🔹 Tool registered: {tool_id}")
            return func

        return decorator

    def get(self, tool_id: str) -> Callable[[Any, InvokeRequest], Any]:
        return self._registry.get(tool_id)


# Singleton instance
tool_executor_registry = ToolExecutorRegistry()

# ---------------------- Document Tools ----------------------
from src.main.python.ir.msob.manak.ai.document.model.document_query_request import DocumentQueryRequest
from src.main.python.ir.msob.manak.ai.document.model.document_overview_response import DocumentOverviewResponse
from src.main.python.ir.msob.manak.ai.document.model.document_chunk_response import DocumentChunkResponse


@tool_executor_registry.register("documentOverviewQuery")
def document_overview_query(service, invoke_request: InvokeRequest) -> DocumentOverviewResponse:
    document_ids: Optional[set[str]] = invoke_request.params.get("documentIds")
    query: str = invoke_request.params.get("query")
    top_k: int = invoke_request.params.get("topK")
    query_request: DocumentQueryRequest = DocumentQueryRequest(document_ids=document_ids, query=query, top_k=top_k)
    return service.document_service.overview_query(query_request)


@tool_executor_registry.register("documentChunkQuery")
def document_chunk_query(service, invoke_request: InvokeRequest) -> DocumentChunkResponse:
    document_ids: Optional[set[str]] = invoke_request.params.get("documentIds")
    query: str = invoke_request.params.get("query")
    top_k: int = invoke_request.params.get("topK")
    query_request: DocumentQueryRequest = DocumentQueryRequest(document_ids=document_ids, query=query, top_k=top_k)
    return service.document_service.chunk_query(query_request)


# ---------------------- Repository Tools ----------------------
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_request import RepositoryQueryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_overview_response import RepositoryOverviewResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_chunk_response import RepositoryChunkResponse


@tool_executor_registry.register("repositoryOverviewQuery")
def repository_overview_query(service, invoke_request: InvokeRequest) -> RepositoryOverviewResponse:
    repository_ids: Optional[set[str]] = invoke_request.params.get("repositoryIds")
    query: str = invoke_request.params.get("query")
    top_k: int = invoke_request.params.get("topK")
    query_request: RepositoryQueryRequest = RepositoryQueryRequest(repository_ids=repository_ids, query=query,
                                                                   top_k=top_k)
    return service.repository_service.overview_query(query_request)


@tool_executor_registry.register("repositoryChunkQuery")
def repository_chunk_query(service, invoke_request: InvokeRequest) -> RepositoryChunkResponse:
    repository_ids: Optional[set[str]] = invoke_request.params.get("repositoryIds")
    query: str = invoke_request.params.get("query")
    top_k: int = invoke_request.params.get("topK")
    query_request: RepositoryQueryRequest = RepositoryQueryRequest(repository_ids=repository_ids, query=query,
                                                                   top_k=top_k)
    return service.repository_service.chunk_query(query_request)
