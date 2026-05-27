from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .fritzbox import FritzDocsis


class FritzDocsisCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry):

        self.entry = entry

        self.api = FritzDocsis(
            entry.data["host"],
            entry.data["username"],
            entry.data["password"],
        )

        super().__init__(
            hass,
            logger=None,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.data["scan_interval"]
            ),
        )

    async def _async_update_data(self):

        return await self.hass.async_add_executor_job(
            self.api.get_docsis_data
        )
