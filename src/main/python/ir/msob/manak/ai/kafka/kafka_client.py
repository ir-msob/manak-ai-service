import json
import logging

from aiokafka import AIOKafkaProducer

from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration

logger = logging.getLogger(__name__)


class KafkaAsyncClient:
    def __init__(self):
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        logger.info(
            f"🚀 Connecting to Kafka at {ConfigConfiguration.get_properties().kafka.producer.bootstrap_servers} ...")
        self.producer = AIOKafkaProducer(
            bootstrap_servers=ConfigConfiguration.get_properties().kafka.producer.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self.producer.start()
        logger.info("✅ Kafka producer started.")

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            logger.info("🛑 Kafka producer stopped.")

    async def send(self, topic: str, key: str, value: dict):
        if not self.producer:
            raise RuntimeError("Kafka producer not started.")
        logger.info(f"📤 Sending message to topic '{topic}' for key '{key}'")
        await self.producer.send_and_wait(topic, key=key.encode("utf-8"), value=value)
        logger.info("✅ Message sent successfully.")
