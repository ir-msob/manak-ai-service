import logging
from fastapi import APIRouter, HTTPException
from functools import wraps
from inspect import iscoroutinefunction

from src.main.python.ir.msob.manak.ai.tool.model.invoke_request import InvokeRequest
from src.main.python.ir.msob.manak.ai.tool.model.invoke_response import InvokeResponse
from src.main.python.ir.msob.manak.ai.tool.tool_service import ToolService

logger = logging.getLogger(__name__)
router = APIRouter()
service = ToolService()


def handle_exceptions(func):
    """Decorator to catch exceptions and log them before raising HTTPException."""
    if iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.exception("❌ Unexpected error in %s: %s", func.__name__, e)
                raise HTTPException(status_code=500, detail=str(e))

        return wrapper
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.exception("❌ Unexpected error in %s: %s", func.__name__, e)
                raise HTTPException(status_code=500, detail=str(e))

        return wrapper


@router.post("/tool/invoke", response_model=InvokeResponse)
@handle_exceptions
def invoke(invoke_request: InvokeRequest) -> InvokeResponse:
    logger.info("🔧 Tool invoke request received: tool_id=%s", invoke_request.tool_id)

    if not invoke_request.tool_id:
        raise HTTPException(status_code=400, detail="Empty tool id")

    result: InvokeResponse = service.invoke(invoke_request)
    logger.info("✅ Tool invocation completed: tool_id=%s", invoke_request.tool_id)
    return result
