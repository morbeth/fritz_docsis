from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class FritzDocsisConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:

        if user_input is not None:

            await self.async_set_unique_id(
                user_input["host"]
            )

            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"FRITZ!Box {user_input['host']}",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "host",
                        default="192.168.178.1",
                    ): str,

                    vol.Optional(
                        "username",
                        default="",
                    ): str,

                    vol.Required(
                        "password",
                    ): str,

                    vol.Required(
                        "scan_interval",
                        default=300,
                    ): int,
                }
            ),
        )
