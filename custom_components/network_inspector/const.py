"""Constants for the Network Inspector integration."""

DOMAIN = "network_inspector"

# Configuration keys
CONF_DEVICE_NAME = "device_name"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_CONSIDER_HOME = "consider_home"
CONF_PING_COUNT = "ping_count"
CONF_PING_TIMEOUT = "ping_timeout"

# Defaults
DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_CONSIDER_HOME = 180  # seconds (3 minutes)
DEFAULT_PING_COUNT = 3
DEFAULT_PING_TIMEOUT = 1  # seconds
DEFAULT_PING_HISTORY_SIZE = 50
