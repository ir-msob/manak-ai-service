import logging

from src.main.python.ir.msob.manak.ai.channel.channel_message import ChannelMessage
from src.main.python.ir.msob.manak.ai.channel.dto_message import DtoMessage
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.domain.user import SYSTEM_USER
from src.main.python.ir.msob.manak.ai.tool.tool_provider_handler import ToolProviderHandler
from src.main.python.ir.msob.manak.ai.tool.model.tool_provider_dto import ToolProviderDto
from src.main.python.ir.msob.manak.ai.kafka.kafka_client import KafkaAsyncClient
from src.main.python.ir.msob.manak.ai.tool.tool_descriptors_factory import get_tool_descriptors

logger = logging.getLogger(__name__)


class ToolProviderPublisher:
    def __init__(self):
        self.kafka_client = KafkaAsyncClient()
        self.tool_provider_handler = ToolProviderHandler()

    async def publish(self):
        logger.info("🚀 Starting tool provider publishing...")
        try:
            await self.kafka_client.start()
            provider: ToolProviderDto = self.tool_provider_handler.get_tool_provider()
            provider.tools = get_tool_descriptors()

            message_dto: DtoMessage = DtoMessage(dto=provider)
            channel_message: ChannelMessage = ChannelMessage(key=provider.name,
                                                             data=message_dto,
                                                             user=SYSTEM_USER,
                                                             channel=ConfigConfiguration.get_properties().tool.tool_provider_topic,
                                                             callbacks=[],
                                                             error_callbacks=[])

            await self.kafka_client.send(
                topic=ConfigConfiguration.get_properties().tool.tool_provider_topic,
                key=provider.name,
                value=channel_message.model_dump(by_alias=True)
            )
            logger.info(f"✅ ToolProvider '{provider.name}' published with {len(provider.tools)} tools.")
        except Exception as e:
            logger.exception("❌ Failed to publish ToolProvider message.")
            raise e
        finally:
            await self.kafka_client.stop()
