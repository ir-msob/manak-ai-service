from pydantic import BaseModel

from src.main.python.ir.msob.manak.ai.tool.model.request_schema import RequestSchema
from src.main.python.ir.msob.manak.ai.tool.model.response_schema import ResponseSchema

# ---------------------------
# Tool Descriptor
# ---------------------------
class ToolDescriptor(BaseModel):
    name: str
    key: str
    description: str
    version: str = "v1"
    input_schema: RequestSchema
    output_schema: ResponseSchema
    status: str = "ACTIVE"  # Could be ACTIVE, INACTIVE, DEPRECATED
