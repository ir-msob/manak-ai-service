import logging
from py_eureka_client import eureka_client
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration


class EurekaServiceManager:
    def __init__(self):
        self.config = ConfigConfiguration().get_properties()
        self._eureka_initialized = False
        self.logger = logging.getLogger("EurekaManager")
        self.logger.setLevel(logging.DEBUG)  # Ensure debug logs are shown

    def is_dev_profile(self) -> bool:
        """Check if dev profile is active"""
        active_profiles = self.config.python.profiles.active
        self.logger.debug(f"Active profiles: {active_profiles}")
        return "dev" in active_profiles

    async def register_to_eureka(self) -> None:
        """Register service with Eureka only in dev profile"""
        self.logger.info("Checking Eureka registration conditions...")

        if not self.is_dev_profile():
            self.logger.info("❌ Eureka connection disabled - not in dev profile")
            return

        if not self.config.python.eureka:
            self.logger.warning("❌ Eureka configuration not found")
            return

        try:
            eureka_config = self.config.python.eureka
            service_url = eureka_config.client.service_url.get("defaultZone", "")

            self.logger.debug(f"Eureka config: {eureka_config}")
            self.logger.debug(f"Service URL: {service_url}")
            self.logger.debug(f"App name: {eureka_config.instance.appname}")
            self.logger.debug(f"Port: {self.config.server.port}")

            if not service_url:
                self.logger.error("❌ Eureka server URL not found")
                return

            self.logger.info(f"🔄 Registering with Eureka at {service_url}...")

            await eureka_client.init_async(
                eureka_server=service_url,
                app_name=eureka_config.instance.appname,
                instance_port=self.config.server.port,
                instance_id=eureka_config.instance.instance_id,
                renewal_interval_in_secs=30,
                duration_in_secs=90,
                # Add more configuration for better debugging
                vip_address=eureka_config.instance.appname,
                host_name=eureka_config.instance.hostname or "localhost",
                data_center_name="MyOwn"
            )

            self._eureka_initialized = True
            self.logger.info(
                f"✅ Service registered with Eureka: {eureka_config.instance.appname}:{self.config.server.port}"
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to register with Eureka: {e}")
            self.logger.exception("Full exception details:")

    async def deregister_from_eureka(self) -> None:
        """Deregister service from Eureka"""
        if self._eureka_initialized:
            try:
                await eureka_client.stop_async()
                self.logger.info("✅ Service deregistered from Eureka")
            except Exception as e:
                self.logger.error(f"❌ Failed to deregister from Eureka: {e}")
        else:
            self.logger.info("ℹ️  Service was not registered with Eureka")

    def get_status(self) -> dict:
        """Get Eureka connection status"""
        return {
            "registered": self._eureka_initialized,
            "dev_profile": self.is_dev_profile(),
            "eureka_configured": self.config.python.eureka is not None,
            "app_name": self.config.python.eureka.instance.appname if self.config.python.eureka else None,
            "port": self.config.server.port
        }