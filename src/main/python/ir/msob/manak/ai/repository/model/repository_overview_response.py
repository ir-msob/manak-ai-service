from typing import List, Optional
from pydantic import Field
from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.repository.model.repository_query_response import RepositoryQueryResponse


class RepositoryOverviewResponse(ResponseModel):
    """
    Response model for repository overview query results.
    """
    repository_ids: Optional[set[str]] = None
    query: str
    top_k: int = 5
    overviews: List[RepositoryQueryResponse] = Field(default_factory=list)
