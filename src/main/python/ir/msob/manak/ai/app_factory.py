import logging
from fastapi import FastAPI

from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.document import document_controller
from src.main.python.ir.msob.manak.ai.lifespan_manager import lifespan
from src.main.python.ir.msob.manak.ai.repository import repository_controller
from src.main.python.ir.msob.manak.ai.tool import tool_controller
from src.main.python.ir.msob.manak.ai.eureka.eureka_manager import EurekaServiceManager

def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    config = ConfigConfiguration().get_properties()
    app = FastAPI(
        title=config.python.application.name,
        lifespan=lifespan,
    )

    # Add health and status endpoints
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    @app.get("/eureka-status")
    async def eureka_status():
        eureka_manager = EurekaServiceManager()
        return eureka_manager.get_status()

    app.include_router(document_controller.router, prefix="/api/v1", tags=["Documents"])
    app.include_router(repository_controller.router, prefix="/api/v1", tags=["Repository"])
    app.include_router(tool_controller.router, prefix="/api/v1", tags=["Tool"])

    logging.getLogger("Application").info(
        f"✅ Application '{app.title}' initialized successfully."
    )
    return app