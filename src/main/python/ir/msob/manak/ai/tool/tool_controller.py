import logging
from datetime import datetime, timezone

from fastapi import APIRouter
from functools import wraps
from inspect import iscoroutinefunction

from src.main.python.ir.msob.manak.ai.tool.model.invoke_request import InvokeRequest
from src.main.python.ir.msob.manak.ai.tool.model.invoke_response import InvokeResponse
from src.main.python.ir.msob.manak.ai.tool.tool_service import ToolService
from src.main.python.ir.msob.manak.ai.tool.util.tool_executor_util import ToolExecutorUtil

logger = logging.getLogger(__name__)
router = APIRouter()
service = ToolService()


def handle_exceptions(func):
    """Decorator to catch exceptions and return InvokeResponse instead of raising HTTPException."""
    if iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.exception("❌ Unexpected error in %s: %s", func.__name__, e)
                tool_id = getattr(kwargs.get("invoke_request"), "tool_id", "unknown")
                return InvokeResponse(
                    tool_id=tool_id,
                    error=ToolExecutorUtil.build_error_response(tool_id, e)
                )

        return wrapper
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception("❌ Unexpected error in %s: %s", func.__name__, e)
                id = getattr(kwargs.get("invoke_request"), "id", "unknown")
                tool_id = getattr(kwargs.get("invoke_request"), "tool_id", "unknown")
                return InvokeResponse(
                    id=id,
                    tool_id=tool_id,
                    error=InvokeResponse.ErrorInfo(
                        code="EXECUTION_ERROR",
                        message=ToolExecutorUtil.build_error_response(tool_id, e)
                    ),
                    executed_at=datetime.now(timezone.utc)
                )

        return wrapper


@router.post("/tool/invoke", response_model=InvokeResponse)
@handle_exceptions
def invoke(invoke_request: InvokeRequest) -> InvokeResponse:
    tool_id = invoke_request.tool_id
    logger.info("🔧 Tool invoke request received: tool_id=%s", tool_id)

    if not invoke_request.tool_id:
        logger.warning("⚠️ Missing tool_id in request")
        return InvokeResponse(
            id=invoke_request.id,
            tool_id=tool_id,
            error=InvokeResponse.ErrorInfo(
                code="EXECUTION_ERROR",
                message=ToolExecutorUtil.build_error_response_with_message(tool_id, "Empty tool id")
            ),
            executed_at=datetime.now(timezone.utc)
        )

    result: InvokeResponse = service.invoke(invoke_request)
    if result.error:
        logger.error("❌ Tool invocation failed: %s - %s", invoke_request.tool_id, result.error)
    else:
        logger.info("✅ Tool invocation completed: tool_id=%s", invoke_request.tool_id)
    return result
