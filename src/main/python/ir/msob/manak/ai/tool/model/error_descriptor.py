from typing import Dict, Any

from pydantic import Field

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


# ---------------------------
# Response Schema
# ---------------------------
class ErrorDescriptor(ResponseModel):
    code: str
    message: str
    retriable: bool
    resolution: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
