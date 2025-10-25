from dataclasses import field
from typing import Any

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


class DocumentQueryResponse(ResponseModel):
    document_id: str
    content: str
    meta: dict[str, Any] = field(default_factory=dict)
