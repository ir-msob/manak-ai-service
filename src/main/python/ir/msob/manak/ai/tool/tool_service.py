import logging
from src.main.python.ir.msob.manak.ai.document.document_service_configuration import DocumentServiceConfiguration
from src.main.python.ir.msob.manak.ai.document.model.document_query_request import DocumentQueryRequest
from src.main.python.ir.msob.manak.ai.document.model.document_query_response import DocumentQueryResponse
from src.main.python.ir.msob.manak.ai.tool.model.invoke_request import InvokeRequest
from src.main.python.ir.msob.manak.ai.tool.model.invoke_response import InvokeResponse

logger = logging.getLogger(__name__)


class ToolService:
    """Service responsible for invoking different tools dynamically."""

    def __init__(self):
        self.document_service = DocumentServiceConfiguration().get_document_service()

    def invoke(self, invoke_request: InvokeRequest) -> InvokeResponse:
        """Invoke a tool safely — never raises exceptions, always returns InvokeResponse."""
        invoke_response = InvokeResponse(
            tool_id=invoke_request.tool_id if invoke_request else None
        )

        try:
            if not invoke_request or not invoke_request.tool_id:
                raise ValueError("invoke_request or tool_id cannot be None")

            logger.info("Invoking tool: %s", invoke_request.tool_id)

            if invoke_request.tool_id == "documentQuery":
                query_request_data = (
                    invoke_request.params.get("queryRequest")
                    if invoke_request.params else None
                )

                if query_request_data is None:
                    raise ValueError("Missing required parameter 'queryRequest' for documentQuery tool")

                query_request : DocumentQueryRequest = (
                    query_request_data
                    if isinstance(query_request_data, DocumentQueryRequest)
                    else DocumentQueryRequest.model_validate(query_request_data)
                )

                logger.debug("Executing document query with params: %s", query_request)

                query_response: DocumentQueryResponse = self.document_service.query(query_request)

                invoke_response.result = query_response
                logger.info("✅ Tool %s executed successfully", invoke_request.tool_id)
                return invoke_response

            raise ValueError(f"Unsupported tool_id: {invoke_request.tool_id}")

        except Exception as e:
            logger.error("❌ Tool invocation failed: %s - %s", invoke_request.tool_id if invoke_request else "unknown", str(e))
            invoke_response.error = str(e)
            return invoke_response
