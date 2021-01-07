from homeassistant import config_entries

from .const import DOMAIN


@config_entries.HANDLERS.register(DOMAIN)
class FlowHandler(config_entries.ConfigFlow):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_abort(reason="already_configured")

    async def async_step_import(self, user_input):
        return self.async_abort(reason="already_configured")
