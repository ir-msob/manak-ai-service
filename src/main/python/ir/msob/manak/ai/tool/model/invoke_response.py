from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from src.main.python.ir.msob.manak.ai.base.response_model import ResponseModel


class InvokeResponse(ResponseModel):
    id: Optional[str] = Field(default=None)
    tool_id: str = Field(..., description="Unique identifier of the invoked tool.")
    result: Optional[Any] = Field(default=None, description="Result of the tool execution.")
    error: Optional["InvokeResponse.ErrorInfo"] = Field(default=None,
                                                        description="Error information if execution failed.")
    logs: List["InvokeResponse.LogEntry"] = Field(default_factory=list, description="Execution logs.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata related to the invocation.")
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                  description="Timestamp when the tool was executed.")

    # ---------------------------
    # Nested Classes
    # ---------------------------
    class ErrorInfo(BaseModel):
        code: Optional[str] = Field(default=None, description="Error code representing the type of failure.")
        message: Optional[str] = Field(default=None, description="Human-readable error message.")
        stack_trace: Optional[str] = Field(default=None, description="Stack trace or additional technical details.")
        details: Dict[str, Any] = Field(default_factory=dict, description="Additional contextual error details.")

    class LogEntry(BaseModel):
        timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),
                                    description="Time when the log was created.")
        level: str = Field(..., description="Log level, e.g., INFO, WARN, ERROR.")
        message: str = Field(..., description="Log message text.")
        context: Dict[str, Any] = Field(default_factory=dict,
                                        description="Additional context or structured data for the log entry.")


InvokeResponse.model_rebuild()
