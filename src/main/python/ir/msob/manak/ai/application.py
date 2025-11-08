import logging
import sys
import uvicorn

from src.main.python.ir.msob.manak.ai.app_factory import create_app
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration


def setup_logging() -> None:
    """Configure global logging settings before Uvicorn starts."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    # تنظیم لاگ برای Uvicorn
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logging.getLogger(name).setLevel(logging.DEBUG)

app = create_app()
logging.getLogger("TestLogger").debug("✅ Logging is active.")

def main() -> None:
    """Start the FastAPI application using Uvicorn programmatically."""
    setup_logging()

    config = ConfigConfiguration().get_properties()
    port = config.server.port

    logger = logging.getLogger("Application")
    logger.info(f"🚀 Starting AI service on port {port} ...")

    uvicorn_config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="debug",
    )
    server = uvicorn.Server(uvicorn_config)
    server.run()


if __name__ == "__main__":
    main()
