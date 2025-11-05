import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.main.python.ir.msob.manak.ai.tool.publisher.publisher_runner import start_tool_provider_publisher
from src.main.python.ir.msob.manak.ai.eureka.eureka_manager import EurekaServiceManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle FastAPI startup and shutdown events."""
    logger = logging.getLogger("Application")

    # Initialize Eureka manager
    eureka_manager = EurekaServiceManager()

    logger.info("🚀 FastAPI application starting up...")

    publisher_task = None
    try:
        # Register with Eureka first
        await eureka_manager.register_to_eureka()

        # Then start other services
        publisher_task = asyncio.create_task(start_tool_provider_publisher())
        logger.debug("🟡 ToolProviderPublisher task started.")
    except Exception as e:
        logger.exception(f"❌ Failed to start services: {e}")

    # Wait until shutdown signal
    yield

    logger.info("🛑 FastAPI application shutting down...")

    # Deregister from Eureka
    await eureka_manager.deregister_from_eureka()

    if publisher_task:
        publisher_task.cancel()
        logger.debug("🧹 ToolProviderPublisher task cancelled.")