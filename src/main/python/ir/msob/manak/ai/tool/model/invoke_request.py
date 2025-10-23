from src.main.python.ir.msob.manak.ai.base.request_model import RequestModel
from typing import Any, Dict


class InvokeRequest(RequestModel):
    tool_id: str
    params: Dict[str, Any] | None = None
