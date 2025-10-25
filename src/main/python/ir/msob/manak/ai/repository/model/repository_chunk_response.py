from typing import List, Optional
from pydantic import Field
from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_response import RepositoryQueryResponse


class RepositoryChunkResponse(ResponseModel):
    """
    Response model for repository chunk-level query results.
    """
    repository_ids: Optional[set[str]] = None
    query: str
    top_k: int = 5
    top_chunks: List[RepositoryQueryResponse] = Field(default_factory=list)
    final_summary: str = ""
