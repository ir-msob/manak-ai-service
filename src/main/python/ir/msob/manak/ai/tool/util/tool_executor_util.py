import json
import logging
import socket
import asyncio
from httpx import RequestError, HTTPStatusError, ConnectError, ConnectTimeout
from typing import Optional

logger = logging.getLogger(__name__)


class ToolExecutorUtil:
    """
    Utility class for building consistent and detailed error responses
    when executing tools.
    """

    DEFAULT_ERROR_MESSAGE = "An unexpected error occurred during tool execution."

    @staticmethod
    def build_error_response(tool_id: Optional[str], error: Exception) -> str:
        """
        Builds a full error response string including tool ID and a resolved message.
        """
        return ToolExecutorUtil.build_error_response_with_message(
            tool_id, ToolExecutorUtil.resolve_error_message(error)
        )

    @staticmethod
    def build_error_response_with_message(tool_id: Optional[str], message: str) -> str:
        """
        Builds a full error response string with a custom message.
        """
        return f"Error executing tool '{tool_id or 'unknown'}': {message}"

    @staticmethod
    def resolve_error_message(error: Exception) -> str:
        """
        Resolves human-readable error message based on exception type.
        """
        if error is None:
            return ToolExecutorUtil.DEFAULT_ERROR_MESSAGE

        try:
            # --- HTTP errors ---
            if isinstance(error, HTTPStatusError):
                response = error.response
                body = response.text or "(empty response body)"
                status = response.status_code
                return f"HTTP {status}: {body}"

            elif isinstance(error, RequestError):
                return ToolExecutorUtil._format_request_error(error)

            # --- Connection / Timeout / Network ---
            elif isinstance(error, (ConnectError, socket.gaierror)):
                return "Unable to connect to remote service."
            elif isinstance(error, ConnectTimeout):
                return "Request timed out while connecting to server."
            elif isinstance(error, asyncio.TimeoutError):
                return "Request timed out while waiting for response."

            # --- Parsing / Validation ---
            elif isinstance(error, json.JSONDecodeError):
                return f"Invalid JSON format: {ToolExecutorUtil._safe_message(error.msg)}"
            elif isinstance(error, ValueError):
                return f"Invalid request: {ToolExecutorUtil._safe_message(str(error))}"
            elif isinstance(error, TypeError):
                return f"Type error: {ToolExecutorUtil._safe_message(str(error))}"

            # --- Default fallback ---
            else:
                return ToolExecutorUtil._safe_message(str(error))

        except Exception as ex:
            # Never fail silently while formatting
            logger.exception("Error while resolving exception message: %s", ex)
            return ToolExecutorUtil.DEFAULT_ERROR_MESSAGE

    @staticmethod
    def _format_request_error(error: RequestError) -> str:
        """
        Handles HTTP client request errors.
        """
        cause = getattr(error, "__cause__", None)
        if isinstance(cause, ConnectTimeout):
            return "Request timed out while connecting to server."
        elif isinstance(cause, ConnectError):
            return "Failed to connect to server."
        elif isinstance(cause, socket.gaierror):
            return f"Unknown host: {cause}"
        return f"HTTP client request failed: {ToolExecutorUtil._safe_message(str(error))}"

    @staticmethod
    def _safe_message(message: Optional[str]) -> str:
        """
        Safely returns a message or the default error message if it's blank.
        """
        if not message or not message.strip():
            return ToolExecutorUtil.DEFAULT_ERROR_MESSAGE
        return message.strip()
