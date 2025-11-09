from typing import List

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.tool.model.example import Example
from src.main.python.ir.msob.manak.ai.tool.model.parameter_descriptor import ParameterDescriptor
from src.main.python.ir.msob.manak.ai.tool.model.response_status import ResponseStatus


# ---------------------------
# Response Schema
# ---------------------------
class ResponseDescriptor(ResponseModel):
    statuses: List[ResponseStatus] = []
    response_schema: ParameterDescriptor
    stream: bool
    examples: List[Example] = []
