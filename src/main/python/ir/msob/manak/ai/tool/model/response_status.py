from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel

# ---------------------------
# Response Schema
# ---------------------------
class ResponseStatus(ResponseModel):
    status: str
    description: str
    contentType: str