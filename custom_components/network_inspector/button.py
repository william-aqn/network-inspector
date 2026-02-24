"""Button platform for Network Inspector — manual ping trigger."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_NAME, DOMAIN
from .coordinator import (
    NetworkInspectorConfigEntry,
    NetworkInspectorCoordinator,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NetworkInspectorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the ping button for Network Inspector."""
    coordinator = entry.runtime_data
    async_add_entities([NetworkInspectorPingButton(entry, coordinator)])


class NetworkInspectorPingButton(
    CoordinatorEntity[NetworkInspectorCoordinator], ButtonEntity
):
    """Button to trigger an immediate ping."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:refresh"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        config_entry: NetworkInspectorConfigEntry,
        coordinator: NetworkInspectorCoordinator,
    ) -> None:
        """Initialize the ping button."""
        super().__init__(coordinator)
        device_name = config_entry.options.get(CONF_DEVICE_NAME, "Unknown")
        self._attr_name = f"{device_name} Ping now"
        self._attr_unique_id = f"{config_entry.entry_id}_ping_button"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
        )

    async def async_press(self) -> None:
        """Handle the button press — trigger immediate ping."""
        await self.coordinator.async_request_refresh()
