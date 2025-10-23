from typing import Optional, List

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse

class DocumentQueryResponse(ResponseModel):
    query: Optional[str] = None
    top_k: int
    overviews: List[DocumentResponse]
    top_chunks: List[DocumentResponse]
    final_summary: str

