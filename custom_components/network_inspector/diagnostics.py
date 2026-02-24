"""Diagnostics support for Network Inspector."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .coordinator import NetworkInspectorConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: NetworkInspectorConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    # Current ping result
    current: dict[str, Any] = {}
    if coordinator.data is not None:
        current = {
            "ip_address": coordinator.data.ip_address,
            "is_alive": coordinator.data.is_alive,
            "round_trip_time_avg": coordinator.data.round_trip_time_avg,
            "packet_loss": coordinator.data.packet_loss,
        }

    # Ping history
    history = [
        {
            "timestamp": entry_hist.timestamp.isoformat(),
            "is_alive": entry_hist.is_alive,
            "rtt_avg": entry_hist.round_trip_time_avg,
            "packet_loss": entry_hist.packet_loss,
        }
        for entry_hist in coordinator.ping_history
    ]

    return {
        "config_entry_options": dict(entry.options),
        "current_state": current,
        "ping_history": history,
        "ping_history_size": len(coordinator.ping_history),
    }
