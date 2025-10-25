from typing import Any, Optional, Dict

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


class RepositoryResponse(ResponseModel):
    # existing repo-level fields (kept for compatibility)
    repository_id: Optional[str] = None
    name: Optional[str] = None
    branch: Optional[str] = None
    indexed_files: Any = None
    overview_id: Any = None

    # document-level / retrieval fields (optional)
    document_id: Optional[str] = None
    content: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    score: Optional[float] = None

    # convenience/parsed fields often useful for chunks
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None

    # source kind: "overview" or "chunk"
    type: Optional[str] = None
