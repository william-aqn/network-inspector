"""Device tracker platform for Network Inspector."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.device_tracker import ScannerEntity, SourceType
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    CONF_CONSIDER_HOME,
    CONF_DEVICE_NAME,
    DEFAULT_CONSIDER_HOME,
    DOMAIN,
)
from .coordinator import (
    NetworkInspectorConfigEntry,
    NetworkInspectorCoordinator,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NetworkInspectorConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up device tracker for Network Inspector."""
    coordinator = entry.runtime_data
    async_add_entities([NetworkInspectorDeviceTracker(entry, coordinator)])


class NetworkInspectorDeviceTracker(
    CoordinatorEntity[NetworkInspectorCoordinator], ScannerEntity
):
    """Representation of a network device being tracked via ping."""

    _attr_has_entity_name = True
    _last_seen: datetime | None = None

    def __init__(
        self,
        config_entry: NetworkInspectorConfigEntry,
        coordinator: NetworkInspectorCoordinator,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self._consider_home_interval = timedelta(
            seconds=int(
                config_entry.options.get(CONF_CONSIDER_HOME, DEFAULT_CONSIDER_HOME)
            )
        )
        device_name = config_entry.options.get(CONF_DEVICE_NAME, "Unknown")
        self._attr_name = device_name
        self._attr_unique_id = f"{config_entry.entry_id}_tracker"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=device_name,
            manufacturer="Network Inspector",
            model="ICMP Ping Tracker",
        )

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.ROUTER

    @property
    def ip_address(self) -> str | None:
        """Return the IP address of the tracked device."""
        if self.coordinator.data is not None:
            return self.coordinator.data.ip_address
        return None

    @property
    def is_connected(self) -> bool:
        """Return true if the device is connected (home)."""
        if self.coordinator.data is not None and self.coordinator.data.is_alive:
            self._last_seen = dt_util.utcnow()

        if self._last_seen is None:
            return False

        return (dt_util.utcnow() - self._last_seen) < self._consider_home_interval

    @property
    def icon(self) -> str:
        """Return the icon based on connection state."""
        return "mdi:lan-connect" if self.is_connected else "mdi:lan-disconnect"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        attrs: dict[str, Any] = {}
        if self.coordinator.data is not None:
            attrs["ip_address"] = self.coordinator.data.ip_address
            if self.coordinator.data.round_trip_time_avg is not None:
                attrs["round_trip_time_avg"] = (
                    self.coordinator.data.round_trip_time_avg
                )
            if self.coordinator.data.packet_loss is not None:
                attrs["packet_loss"] = self.coordinator.data.packet_loss
        if self._last_seen is not None:
            attrs["last_seen"] = self._last_seen.isoformat()
        return attrs if attrs else None
