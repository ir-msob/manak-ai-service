from datetime import datetime
from typing import Optional

from src.main.python.ir.msob.manak.ai.base.normalized_model import NormalizedModel


class AuditInfo(NormalizedModel):
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    last_modified_at: Optional[datetime] = None
