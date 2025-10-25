from typing import Optional, List
from pydantic import Field

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.repository.model.repository_response import RepositoryResponse


class RepositoryQueryResponse(ResponseModel):
    query: Optional[str] = None
    top_k: int = 5
    input_overview: Optional[str] = None
    overviews: List[RepositoryResponse] = Field(default_factory=list)
    top_chunks: List[RepositoryResponse] = Field(default_factory=list)
    final_summary: Optional[str] = None
    repo_ids: List[str] = Field(default_factory=list)
