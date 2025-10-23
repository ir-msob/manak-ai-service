from typing import Optional

from src.main.python.ir.msob.manak.ai.base.normalized_model import NormalizedModel
from src.main.python.ir.msob.manak.ai.domain.audit_info import AuditInfo
from src.main.python.ir.msob.manak.ai.domain.time_period import TimePeriod


class RelatedAction(NormalizedModel):
    id: Optional[str] = None
    name: str
    status: str
    mandatory: bool
    valid_for: Optional[TimePeriod] = None
    audit_info: Optional[AuditInfo] = None
