import logging
from typing import Callable, Any
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
    query_data = invoke_request.params.get("queryRequest")
    query_request = query_data if isinstance(query_data, DocumentQueryRequest) else DocumentQueryRequest.model_validate(query_data)
    return service.document_service.overview_query(query_request)

@tool_executor_registry.register("documentChunkQuery")
def document_chunk_query(service, invoke_request: InvokeRequest) -> DocumentChunkResponse:
    query_data = invoke_request.params.get("queryRequest")
    query_request = query_data if isinstance(query_data, DocumentQueryRequest) else DocumentQueryRequest.model_validate(query_data)
    return service.document_service.chunk_query(query_request)


# ---------------------- Repository Tools ----------------------
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_request import RepositoryQueryRequest
from src.main.python.ir.msob.manak.ai.repository.model.repository_overview_response import RepositoryOverviewResponse
from src.main.python.ir.msob.manak.ai.repository.model.repository_chunk_response import RepositoryChunkResponse

@tool_executor_registry.register("repositoryOverviewQuery")
def repository_overview_query(service, invoke_request: InvokeRequest) -> RepositoryOverviewResponse:
    query_data = invoke_request.params.get("queryRequest")
    query_request = query_data if isinstance(query_data, RepositoryQueryRequest) else RepositoryQueryRequest.model_validate(query_data)
    return service.repository_service.overview_query(query_request)

@tool_executor_registry.register("repositoryChunkQuery")
def repository_chunk_query(service, invoke_request: InvokeRequest) -> RepositoryChunkResponse:
    query_data = invoke_request.params.get("queryRequest")
    query_request = query_data if isinstance(query_data, RepositoryQueryRequest) else RepositoryQueryRequest.model_validate(query_data)
    return service.repository_service.chunk_query(query_request)
