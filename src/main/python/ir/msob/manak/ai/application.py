import logging
import sys

import uvicorn
from fastapi import FastAPI

from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.document import document_controller
from src.main.python.ir.msob.manak.ai.repository import repository_controller
from src.main.python.ir.msob.manak.ai.tool import tool_controller


def setup_logging() -> None:
    """Configure global logging settings."""
    logging.basicConfig(
        level=logging.DEBUG,  # Show all logs: DEBUG and above
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )

    # Ensure Uvicorn logs also show DEBUG messages
    uvicorn_loggers = ["uvicorn", "uvicorn.error", "uvicorn.access"]
    for name in uvicorn_loggers:
        logging.getLogger(name).setLevel(logging.DEBUG)


def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    # 🔹 Load configuration
    config = ConfigConfiguration().get_properties()

    # 🔹 Initialize FastAPI app
    app = FastAPI(title=config.python.application.name)

    # 🔹 Register routes
    app.include_router(document_controller.router, prefix="/api/v1", tags=["Documents"])
    app.include_router(repository_controller.router, prefix="/api/v1", tags=["Repository"])
    app.include_router(tool_controller.router, prefix="/api/v1", tags=["Tool"])

    logging.getLogger("Application").info(f"✅ Application '{app.title}' initialized successfully.")
    return app


app = create_app()


def main() -> None:
    """Start the FastAPI application using Uvicorn."""
    setup_logging()
    port = ConfigConfiguration().get_properties().server.port
    logging.getLogger("Application").info(f"🚀 Starting AI service on port {port} ...")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="debug",  # Ensure Uvicorn logs all messages
    )


if __name__ == "__main__":
    main()
