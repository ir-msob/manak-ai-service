from typing import Optional, List

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.repository.model.repository_response import RepositoryResponse


class RepositoryQueryResponse(ResponseModel):
    query: Optional[str] = None
    top_k: int
    input_overview: Optional[str] = None
    overviews: List[RepositoryResponse]
    top_chunks: List[RepositoryResponse]
