# Network Inspector

Custom Home Assistant integration for presence detection via ICMP ping.

## Features

- Track device presence by pinging IP addresses
- Configurable polling interval per device
- Configurable "consider home" grace period before marking as away
- Manual ping button for immediate status check
- Diagnostic sensor with ping history (last 50 results)
- Full diagnostics download support

## Installation via HACS

1. Open HACS in your Home Assistant
2. Go to **Integrations**
3. Click the three dots menu (top right) → **Custom repositories**
4. Add this repository URL and select category **Integration**
5. Click **Add**
6. Find **Network Inspector** in the list and click **Download**
7. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** → search for **Network Inspector**
3. Enter:
   - **IP address** — device IP to ping
   - **Device name** — friendly name
   - **Polling interval** — how often to ping (default: 30s)
   - **Consider home interval** — grace period before marking as away (default: 180s)

Repeat for each device you want to track.

## Entities created per device

| Entity | Description |
|--------|-------------|
| `device_tracker.*` | Presence state: `home` / `not_home` |
| `button.*_ping_now` | Manual ping trigger |
| `sensor.*_ping_log` | Last ping status + history in attributes |

## Options

After adding a device, click **Configure** to adjust:
- Polling interval
- Consider home interval
- Ping count (ICMP packets per poll)
- Ping timeout
