"""DataUpdateCoordinator for the Network Inspector integration."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from icmplib import NameLookupError, SocketPermissionError, async_ping

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PING_COUNT,
    CONF_PING_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PING_COUNT,
    DEFAULT_PING_HISTORY_SIZE,
    DEFAULT_PING_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

type NetworkInspectorConfigEntry = ConfigEntry[NetworkInspectorCoordinator]


@dataclass(slots=True, frozen=True)
class PingResult:
    """Data returned by a ping poll."""

    ip_address: str
    is_alive: bool
    round_trip_time_avg: float | None
    packet_loss: float | None


@dataclass(slots=True, frozen=True)
class PingHistoryEntry:
    """A single entry in the ping history buffer."""

    timestamp: datetime
    is_alive: bool
    round_trip_time_avg: float | None
    packet_loss: float | None


class NetworkInspectorCoordinator(DataUpdateCoordinator[PingResult]):
    """Coordinator that polls a single IP address via ICMP ping."""

    config_entry: NetworkInspectorConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: NetworkInspectorConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self._ip_address: str = config_entry.options[CONF_HOST]
        self._ping_count: int = int(
            config_entry.options.get(CONF_PING_COUNT, DEFAULT_PING_COUNT)
        )
        self._ping_timeout: int = int(
            config_entry.options.get(CONF_PING_TIMEOUT, DEFAULT_PING_TIMEOUT)
        )
        scan_interval = int(
            config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )

        self.ping_history: deque[PingHistoryEntry] = deque(
            maxlen=DEFAULT_PING_HISTORY_SIZE
        )

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{DOMAIN} {self._ip_address}",
            update_interval=timedelta(seconds=scan_interval),
        )

    @property
    def ip_address(self) -> str:
        """Return the target IP address."""
        return self._ip_address

    async def _async_update_data(self) -> PingResult:
        """Ping the target IP and return the result."""
        try:
            result = await async_ping(
                self._ip_address,
                count=self._ping_count,
                timeout=self._ping_timeout,
                privileged=False,
            )
        except NameLookupError as err:
            _LOGGER.debug(
                "Name lookup failed for %s: %s", self._ip_address, err
            )
            ping_result = PingResult(
                ip_address=self._ip_address,
                is_alive=False,
                round_trip_time_avg=None,
                packet_loss=100.0,
            )
            self._record_history(ping_result)
            return ping_result
        except SocketPermissionError as err:
            raise UpdateFailed(
                f"Insufficient permissions for ICMP ping: {err}"
            ) from err
        except OSError as err:
            raise UpdateFailed(
                f"Error pinging {self._ip_address}: {err}"
            ) from err

        ping_result = PingResult(
            ip_address=self._ip_address,
            is_alive=result.is_alive,
            round_trip_time_avg=round(result.avg_rtt, 2) if result.is_alive else None,
            packet_loss=round(result.packet_loss * 100, 1),
        )
        self._record_history(ping_result)
        return ping_result

    def _record_history(self, result: PingResult) -> None:
        """Record a ping result in the history buffer."""
        self.ping_history.append(
            PingHistoryEntry(
                timestamp=dt_util.utcnow(),
                is_alive=result.is_alive,
                round_trip_time_avg=result.round_trip_time_avg,
                packet_loss=result.packet_loss,
            )
        )
