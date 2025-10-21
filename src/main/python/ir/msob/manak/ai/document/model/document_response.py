from typing import Dict, Any
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    file_path: str = ""
    filename: str = ""
    file_type: str = ""
    meta: Dict[str, Any] = Field(default_factory=dict)
    content: str = ""

    model_config = {
        "arbitrary_types_allowed": True
    }
