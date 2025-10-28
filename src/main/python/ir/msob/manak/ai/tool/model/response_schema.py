from typing import Dict, Optional
from pydantic import BaseModel, Field
from src.main.python.ir.msob.manak.ai.tool.model.tool_parameter import ToolParameter

# ---------------------------
# Response Schema
# ---------------------------
class ResponseSchema(BaseModel):
    tool_id: ToolParameter
    res: Dict[str, ToolParameter] = Field(default_factory=dict)
    error: Optional[ToolParameter] = None