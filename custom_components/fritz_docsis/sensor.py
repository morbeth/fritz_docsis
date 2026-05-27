from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    entities.append(
        Docsis31MerSensor(coordinator)
    )

    entities.append(
        Docsis31PowerSensor(coordinator)
    )

    entities.append(
        DocsisUncorrectableSensor(coordinator)
    )

    async_add_entities(entities)


class Docsis31MerSensor(CoordinatorEntity, SensorEntity):

    _attr_name = "DOCSIS 3.1 MER"
    _attr_native_unit_of_measurement = "dB"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        return self.coordinator.data["docsis31"].get("mer")

    @property
    def unique_id(self):
        return "fritz_docsis_31_mer"


class Docsis31PowerSensor(CoordinatorEntity, SensorEntity):

    _attr_name = "DOCSIS 3.1 Power"
    _attr_native_unit_of_measurement = "dBmV"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        return self.coordinator.data["docsis31"].get("power")

    @property
    def unique_id(self):
        return "fritz_docsis_31_power"


class DocsisUncorrectableSensor(CoordinatorEntity, SensorEntity):

    _attr_name = "DOCSIS Nicht korrigierbare Fehler"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):

        total = 0

        for channel in self.coordinator.data["docsis30"]:
            total += channel["uncorrectable"]

        return total

    @property
    def unique_id(self):
        return "fritz_docsis_uncorrectable"
