from src.main.python.ir.msob.manak.ai.base.request_model import RequestModel
from typing import Any, Dict

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


class DtoMessage(ResponseModel):
    id: str | None = None
    dto: Any | None = None
    classType: str = "DtoMessage"
