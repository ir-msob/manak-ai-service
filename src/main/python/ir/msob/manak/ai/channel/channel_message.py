from src.main.python.ir.msob.manak.ai.base.request_model import RequestModel
from typing import Any, Dict, List

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.domain.user import User


class ChannelMessage(ResponseModel):
    key: str | None = None
    metadata: Dict[str,Any] | None = None
    user: User | None = None
    data: Any | None = None
    status: int | None = None
    channel: str | None = None
    callbacks: List[Any] | None = []
    error_callbacks: List[Any] | None = []
    classType: str = "ChannelMessage"
