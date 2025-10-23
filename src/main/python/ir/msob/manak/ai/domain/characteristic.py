from typing import Optional

from src.main.python.ir.msob.manak.ai.base.normalized_model import NormalizedModel


class Characteristic(NormalizedModel):
    id: Optional[str] = None
    name: str
    value: str
    value_type: str