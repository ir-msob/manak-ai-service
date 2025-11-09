from typing import Dict, Any

from pydantic import Field

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


# ---------------------------
# Response Schema
# ---------------------------
class Example(ResponseModel):
    title: str
    description: str
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Dict[str, Any] = Field(default_factory=dict)
