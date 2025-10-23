from typing import Any, Dict

from pydantic import Field

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


class RepositoryResponse(ResponseModel):
    repository_id: str
    name: str
    meta: Dict[str, Any] = Field(default_factory=dict)
