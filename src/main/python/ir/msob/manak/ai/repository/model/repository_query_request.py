from src.main.python.ir.msob.manak.ai.base.request_model import RequestModel

class RepositoryQueryRequest(RequestModel):
    query: str
    top_k: int = 5