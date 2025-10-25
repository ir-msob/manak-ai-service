from typing import List, Optional

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.document.model.document_query_response import DocumentQueryResponse


class DocumentChunkResponse(ResponseModel):
    document_ids: Optional[set[str]] = None
    query: str
    top_k: int
    top_chunks: List[DocumentQueryResponse] = []
    final_summary: Optional[str] = ""
