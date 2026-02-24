"""Sensor platform for Network Inspector — debug ping log."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_NAME
from .coordinator import (
    NetworkInspectorConfigEntry,
    NetworkInspectorCoordinator,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NetworkInspectorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the ping log sensor for Network Inspector."""
    coordinator = entry.runtime_data
    async_add_entities([NetworkInspectorLogSensor(entry, coordinator)])


class NetworkInspectorLogSensor(
    CoordinatorEntity[NetworkInspectorCoordinator], SensorEntity
):
    """Sensor showing the latest ping status and history."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:text-box-search-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        config_entry: NetworkInspectorConfigEntry,
        coordinator: NetworkInspectorCoordinator,
    ) -> None:
        """Initialize the log sensor."""
        super().__init__(coordinator)
        device_name = config_entry.options.get(CONF_DEVICE_NAME, "Unknown")
        self._attr_name = f"{device_name} Ping log"
        self._attr_unique_id = f"{config_entry.entry_id}_ping_log"

    @property
    def native_value(self) -> str | None:
        """Return a short status of the last ping."""
        if self.coordinator.data is None:
            return None

        data = self.coordinator.data
        if data.is_alive:
            rtt = data.round_trip_time_avg
            return f"OK {rtt}ms" if rtt is not None else "OK"

        loss = data.packet_loss
        return f"FAIL {loss}% loss" if loss is not None else "FAIL"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the ping history as attributes."""
        if not self.coordinator.ping_history:
            return None

        history = [
            {
                "timestamp": entry.timestamp.isoformat(),
                "is_alive": entry.is_alive,
                "rtt_avg": entry.round_trip_time_avg,
                "packet_loss": entry.packet_loss,
            }
            for entry in self.coordinator.ping_history
        ]

        return {"ping_history": history}
