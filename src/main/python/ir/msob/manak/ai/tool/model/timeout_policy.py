from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


# ---------------------------
# Response Schema
# ---------------------------
class TimeoutPolicy(ResponseModel):
    timeout_ms: int
    fail_fast: bool
    grace_period_ms: int

