import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.main.python.ir.msob.manak.ai.tool.publisher_runner import start_tool_provider_publisher


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle FastAPI startup and shutdown events."""
    logger = logging.getLogger("Application")

    logger.info("🚀 FastAPI application starting up...")

    publisher_task = None
    try:
        publisher_task = asyncio.create_task(start_tool_provider_publisher())
        logger.debug("🟡 ToolProviderPublisher task started.")
    except Exception as e:
        logger.exception(f"❌ Failed to start ToolProviderPublisher: {e}")

    # Wait until shutdown signal
    yield

    logger.info("🛑 FastAPI application shutting down...")
    if publisher_task:
        publisher_task.cancel()
        logger.debug("🧹 ToolProviderPublisher task cancelled.")
