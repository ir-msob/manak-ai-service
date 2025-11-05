import logging
from src.main.python.ir.msob.manak.ai.tool.model.invoke_request import InvokeRequest
from src.main.python.ir.msob.manak.ai.tool.model.invoke_response import InvokeResponse
from src.main.python.ir.msob.manak.ai.tool.tool_executor_registry import tool_executor_registry
from src.main.python.ir.msob.manak.ai.tool.util.tool_executor_util import ToolExecutorUtil

logger = logging.getLogger(__name__)

class ToolService:
    """Dynamic tool invocation service using registry."""

    def __init__(self):
        from src.main.python.ir.msob.manak.ai.document.document_service_configuration import DocumentServiceConfiguration
        from src.main.python.ir.msob.manak.ai.repository.repository_service_configuration import RepositoryServiceConfiguration

        self.document_service = DocumentServiceConfiguration().get_document_service()
        self.repository_service = RepositoryServiceConfiguration().get_repository_service()

    def invoke(self, invoke_request: InvokeRequest) -> InvokeResponse:
        response = InvokeResponse(tool_id=invoke_request.tool_id if invoke_request else None)

        try:
            if not invoke_request or not invoke_request.tool_id:
                raise ValueError("invoke_request or tool_id cannot be None")

            handler = tool_executor_registry.get(invoke_request.tool_id)
            if not handler:
                raise ValueError(f"Unsupported tool_id: {invoke_request.tool_id}")

            logger.info(f"🟢 Invoking tool: {invoke_request.tool_id}")
            response.result = handler(self, invoke_request)
            logger.info(f"✅ Tool {invoke_request.tool_id} executed successfully")
            return response

        except Exception as e:
            logger.exception(
                "❌ Tool invocation failed: %s - %s",
                invoke_request.tool_id if invoke_request else "unknown",
                str(e)
            )
            error_message = ToolExecutorUtil.build_error_response(
                invoke_request.tool_id if invoke_request else "unknown", e)
            logger.error(error_message, exc_info=True)
            response.error = error_message
            return response
