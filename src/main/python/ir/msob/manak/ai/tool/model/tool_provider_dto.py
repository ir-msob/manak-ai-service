from typing import List, Optional
from pydantic import BaseModel, Field
from src.main.python.ir.msob.manak.ai.tool.model.tool_descriptor import ToolDescriptor

# ---------------------------
# Tool Provider DTO
# ---------------------------
class ToolProviderDto(BaseModel):
    name: str
    description: Optional[str] = None
    base_url: str
    endpoint: str
    tools: List[ToolDescriptor] = Field(default_factory=list)
