import logging

from fastapi import APIRouter, HTTPException

from src.main.python.ir.msob.manak.ai.tool.model.invoke_request import InvokeRequest
from src.main.python.ir.msob.manak.ai.tool.model.invoke_response import InvokeResponse
from src.main.python.ir.msob.manak.ai.tool.tool_service import ToolService

logger = logging.getLogger(__name__)
router = APIRouter()
service = ToolService()


@router.post("/invoke", response_model=InvokeResponse)
def query_text(invoke_request: InvokeRequest):
    if not invoke_request.tool_id:
        raise HTTPException(status_code=400, detail="Empty tool id")
    try:
        result = service.invoke(invoke_request)
        return result
    except Exception as e:
        logger.exception("Error querying text: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
