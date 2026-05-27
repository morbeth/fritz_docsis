from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .fritzbox import FritzDocsis

LOGGER = logging.getLogger(__name__)


class FritzDocsisCoordinator(
    DataUpdateCoordinator,
):

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ):

        self.entry = entry

        self.api = FritzDocsis(
            entry.data["host"],
            entry.data.get("username", ""),
            entry.data["password"],
        )

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.data["scan_interval"]
            ),
        )

    async def _async_update_data(self):

        return await self.hass.async_add_executor_job(
            self.api.get_docsis_data
        )
