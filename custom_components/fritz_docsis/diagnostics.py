async def async_get_config_entry_diagnostics(hass, entry):

    coordinator = hass.data["fritz_docsis"][entry.entry_id]

    return coordinator.data
