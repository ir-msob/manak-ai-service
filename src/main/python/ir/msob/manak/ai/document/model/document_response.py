from typing import Any, Dict

from pydantic import Field

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


class DocumentResponse(ResponseModel):
    document_id: str
    file_path: str = ""
    file_name: str = ""
    mime_type: str = ""
    meta: Dict[str, Any] = Field(default_factory=dict)
