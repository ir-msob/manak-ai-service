from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


# ---------------------------
# Response Schema
# ---------------------------
class RetryPolicy(ResponseModel):
    enabled: bool
    max_attempts: int
    initial_interval_ms: int
    multiplier: float
    max_interval_ms: int
    retry_on_status: set[int] = []
    retry_on_error_codes: set[str] = []
