from typing import Any
from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


class InvokeResponse(ResponseModel):
    tool_id: str
    result: Any = None
    error: str = None
