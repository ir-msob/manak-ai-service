import asyncio
import logging
from src.main.python.ir.msob.manak.ai.tool.publisher.tool_provider_publisher import ToolProviderPublisher


async def start_tool_provider_publisher():
    """Start the Tool Provider Publisher in background."""
    logger = logging.getLogger("Publisher")
    try:
        publisher = ToolProviderPublisher()
        logger.info("🟡 Starting ToolProviderPublisher...")
        await publisher.publish()
        logger.info("✅ ToolProviderPublisher finished successfully.")
    except asyncio.CancelledError:
        logger.warning("⚠️ ToolProviderPublisher was cancelled.")
    except Exception as e:
        logger.exception(f"❌ ToolProviderPublisher failed: {e}")
