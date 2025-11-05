from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.tool.model.tool_provider_dto import ToolProviderDto

class ToolProviderHandler:
    def __init__(self):
        pass

    def get_tool_provider(self) -> ToolProviderDto:
        return ToolProviderDto(
            name=ConfigConfiguration.get_properties().python.application.name,
            description=f"ToolProvider for Python Service: {ConfigConfiguration.get_properties().python.application.name}",
            service_name=ConfigConfiguration.get_properties().python.application.name,
            endpoint="/api/v1/tool/invoke"
        )
