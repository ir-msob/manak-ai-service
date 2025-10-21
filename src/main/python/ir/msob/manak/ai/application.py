import logging

import uvicorn
from fastapi import FastAPI

from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.document import document_controller


def setup_logging() -> None:
    """Configure global logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    # 🔹 Load configuration
    config = ConfigConfiguration().get_properties()

    # 🔹 Initialize FastAPI app
    app = FastAPI(title=config.python.application.name)

    # 🔹 Register routes
    app.include_router(document_controller.router, prefix="/api/v1/documents", tags=["Documents"])

    logging.getLogger("Application").info(f"✅ Application '{app.title}' initialized successfully.")

    return app


app = create_app()


def main() -> None:
    """Start the FastAPI application using Uvicorn."""
    setup_logging()
    port = ConfigConfiguration().get_properties().server.port
    logging.getLogger("Application").info(f"🚀 Starting AI service on port {port} ...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
