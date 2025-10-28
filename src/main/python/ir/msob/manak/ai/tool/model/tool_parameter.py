from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


# ---------------------------
# Tool Parameter
# ---------------------------
class ToolParameter(BaseModel):
    type: str  # string, number, boolean, object, array
    description: str
    default_value: Optional[Any] = None
    example: Optional[Any] = None
    required: bool = True