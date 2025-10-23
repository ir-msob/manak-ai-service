from typing import Optional

from src.main.python.ir.msob.manak.ai.base.normalized_model import NormalizedModel
from src.main.python.ir.msob.manak.ai.domain.time_period import TimePeriod


class ObjectValidation(NormalizedModel):
    id: Optional[str] = None
    name: str
    status: str
    enabled: bool
    valid_for: Optional[TimePeriod] = None