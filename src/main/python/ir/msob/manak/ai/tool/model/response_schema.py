from typing import Dict, Optional
from pydantic import BaseModel, Field

from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel
from src.main.python.ir.msob.manak.ai.tool.model.tool_parameter import ToolParameter

# ---------------------------
# Response Schema
# ---------------------------
class ResponseSchema(ResponseModel):
    tool_id: ToolParameter
    res: ToolParameter
    error: ToolParameter