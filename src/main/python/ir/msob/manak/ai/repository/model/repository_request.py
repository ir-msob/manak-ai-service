from src.main.python.ir.msob.manak.ai.base.request_model import RequestModel


class RepositoryRequest(RequestModel):
    repository_id: str
    branch: str
