from typing import Any, Optional, Dict
from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


class RepositoryQueryResponse(ResponseModel):
    """
    Unified response model for both overview and chunk retrieval results.
    """

    # Repository-level info
    repository_id: Optional[str] = None
    name: Optional[str] = None
    branch: Optional[str] = None
    indexed_files: Any = None
    overview_id: Any = None

    # Document-level info
    document_id: Optional[str] = None
    content: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    score: Optional[float] = None

    # Chunk info (if applicable)
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None

    # Type indicator: "overview" or "chunk"
    type: Optional[str] = None
