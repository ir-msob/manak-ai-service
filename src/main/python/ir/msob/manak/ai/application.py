import logging
import uvicorn

from src.main.python.ir.msob.manak.ai.app_factory import create_app
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.logging_config import setup_logging

app = create_app()


def main() -> None:
    """Start the FastAPI application using Uvicorn."""
    setup_logging()
    config = ConfigConfiguration().get_properties()
    port = config.server.port
    logging.getLogger("Application").info(f"🚀 Starting AI service on port {port} ...")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="debug",
    )


if __name__ == "__main__":
    main()
