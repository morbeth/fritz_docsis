from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        DocsisSignalProblemBinarySensor(coordinator)
    ])


class DocsisSignalProblemBinarySensor(
    CoordinatorEntity,
    BinarySensorEntity,
):

    _attr_name = "DOCSIS Signalproblem"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def is_on(self):

        mer = self.coordinator.data["docsis31"].get("mer", 40)

        if mer < 35:
            return True

        return False

    @property
    def unique_id(self):
        return "fritz_docsis_signal_problem"
