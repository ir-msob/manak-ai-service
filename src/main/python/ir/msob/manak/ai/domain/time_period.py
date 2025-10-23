from datetime import datetime
from typing import Optional

from src.main.python.ir.msob.manak.ai.base.normalized_model import NormalizedModel


class TimePeriod(NormalizedModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
