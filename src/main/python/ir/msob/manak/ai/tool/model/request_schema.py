from typing import Dict

from pydantic import BaseModel, Field

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.tool.model.tool_parameter import ToolParameter


# ---------------------------
# Request Schema
# ---------------------------
class RequestSchema(ResponseModel):
    tool_id: ToolParameter
    params: Dict[str, ToolParameter] = Field(default_factory=dict)