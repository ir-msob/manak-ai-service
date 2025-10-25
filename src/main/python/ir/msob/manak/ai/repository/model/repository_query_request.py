from typing import Optional

from src.main.python.ir.msob.manak.ai.base.request_model import RequestModel


class RepositoryQueryRequest(RequestModel):
    """
    Request model for querying repository data.
    """
    repository_ids: Optional[set[str]] = None
    query: str
    top_k: int = 5
