from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .coordinator import FritzDocsisCoordinator


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):

    coordinator: FritzDocsisCoordinator = (
        entry.runtime_data
    )

    async_add_entities(
        [
            Docsis31MerSensor(coordinator),
            Docsis31PowerSensor(coordinator),
        ]
    )


class Docsis31MerSensor(
    CoordinatorEntity,
    SensorEntity,
):

    _attr_has_entity_name = True
    _attr_name = "DOCSIS 3.1 MER"
    _attr_native_unit_of_measurement = "dB"

    def __init__(self, coordinator):

        super().__init__(coordinator)

        self._attr_unique_id = (
            "fritz_docsis_31_mer"
        )

    @property
    def native_value(self):

        return self.coordinator.data[
            "docsis31"
        ].get("mer")


class Docsis31PowerSensor(
    CoordinatorEntity,
    SensorEntity,
):

    _attr_has_entity_name = True
    _attr_name = "DOCSIS 3.1 Power"
    _attr_native_unit_of_measurement = (
        "dBmV"
    )

    def __init__(self, coordinator):

        super().__init__(coordinator)

        self._attr_unique_id = (
            "fritz_docsis_31_power"
        )

    @property
    def native_value(self):

        return self.coordinator.data[
            "docsis31"
        ].get("power")
