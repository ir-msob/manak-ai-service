import logging
from pathlib import Path

from fastapi import FastAPI
import uvicorn

from src.main.python.ir.msob.manak.ai.config.config import ConfigLoader
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
    config_path = Path(__file__).resolve().parent / "resources/config/config.yaml"
    config = ConfigLoader(path=config_path).get_config()

    # 🔹 Initialize FastAPI app
    app = FastAPI(title=config.python.application.name)

    # 🔹 Register routes
    app.include_router(document_controller.router, prefix="/api/v1/documents", tags=["Documents"])

    logging.getLogger("Application").info(f"✅ Application '{app.title}' initialized successfully.")

    return app


app = create_app()  # فقط FastAPI app تعریف می‌شود


def main() -> None:
    """Start the FastAPI application using Uvicorn."""
    setup_logging()
    config_path = Path(__file__).resolve().parent / "resources/config/config.yaml"
    config = ConfigLoader(path=config_path).get_config()
    port = config.server.port
    logging.getLogger("Application").info(f"🚀 Starting AI service on port {port} ...")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
