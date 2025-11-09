from typing import List, Dict

from pydantic import Field

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.tool.model.error_descriptor import ErrorDescriptor
from src.main.python.ir.msob.manak.ai.tool.model.example import Example
from src.main.python.ir.msob.manak.ai.tool.model.parameter_descriptor import ParameterDescriptor
from src.main.python.ir.msob.manak.ai.tool.model.response_descriptor import ResponseDescriptor
from src.main.python.ir.msob.manak.ai.tool.model.retry_policy import RetryPolicy
from src.main.python.ir.msob.manak.ai.tool.model.timeout_policy import TimeoutPolicy


# ---------------------------
# Tool Descriptor
# ---------------------------
class ToolDescriptor(ResponseModel):
    name: str
    displayName: str
    category: str
    version: str = "v1"
    tags: List[str] = []
    description: str
    parameters: Dict[str, ParameterDescriptor] = Field(default_factory=dict)
    response: ResponseDescriptor
    examples: List[Example] = []
    errors: List[ErrorDescriptor] = []
    retryPolicy : RetryPolicy | None =None
    timeoutPolicy: TimeoutPolicy | None =None
    status: str = "ACTIVE"  # Could be ACTIVE, INACTIVE, DEPRECATED
