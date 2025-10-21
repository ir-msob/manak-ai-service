from typing import Optional, List

from pydantic import BaseModel

from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse


class TextQueryResponse(BaseModel):
    query: Optional[str] = None
    top_k: int
    input_overview: Optional[str] = None
    overviews: List[DocumentResponse]
    top_chunks: List[DocumentResponse]
    final_summary: str

    model_config = {
        "arbitrary_types_allowed": True
    }

