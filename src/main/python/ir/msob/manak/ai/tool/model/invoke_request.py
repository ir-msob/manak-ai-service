from datetime import datetime
from typing import Any, Dict

from src.main.python.ir.msob.manak.ai.base.request_model import RequestModel


class InvokeRequest(RequestModel):
    id: str
    tool_id: str
    parameters: Dict[str, Any] | None = None
    context: Dict[str, Any] | None = None
    metadata: Dict[str, Any] | None = None
    timestamp: datetime | None = None
