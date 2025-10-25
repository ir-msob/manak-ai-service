from typing import Optional

from src.main.python.ir.msob.manak.ai.base.request_model import RequestModel


class DocumentQueryRequest(RequestModel):
    document_ids: Optional[set[str]] = None
    query: str
    top_k: int = 5
