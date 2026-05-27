import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class FritzDocsisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:

            return self.async_create_entry(
                title=f"FRITZ!Box {user_input['host']}",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("host", default="192.168.178.1"): str,
                vol.Optional("username", default=""): str,
                vol.Required("password"): str,
                vol.Required("scan_interval", default=300): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
