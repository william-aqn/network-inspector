"""Config flow for Network Inspector integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.util.network import is_ip_address

from .const import (
    CONF_CONSIDER_HOME,
    CONF_DEVICE_NAME,
    CONF_PING_COUNT,
    CONF_PING_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_CONSIDER_HOME,
    DEFAULT_PING_COUNT,
    DEFAULT_PING_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class NetworkInspectorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Network Inspector."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()

            if not is_ip_address(user_input[CONF_HOST]):
                errors["base"] = "invalid_ip_address"
            else:
                self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})

                return self.async_create_entry(
                    title=user_input[CONF_DEVICE_NAME],
                    data={},
                    options={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME],
                        CONF_SCAN_INTERVAL: int(
                            user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                        ),
                        CONF_CONSIDER_HOME: int(
                            user_input.get(CONF_CONSIDER_HOME, DEFAULT_CONSIDER_HOME)
                        ),
                        CONF_PING_COUNT: DEFAULT_PING_COUNT,
                        CONF_PING_TIMEOUT: DEFAULT_PING_TIMEOUT,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_DEVICE_NAME): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=10,
                            max=300,
                            step=5,
                            unit_of_measurement="seconds",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_CONSIDER_HOME,
                        default=DEFAULT_CONSIDER_HOME,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=600,
                            step=10,
                            unit_of_measurement="seconds",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> NetworkInspectorOptionsFlow:
        """Create the options flow."""
        return NetworkInspectorOptionsFlow()


class NetworkInspectorOptionsFlow(OptionsFlowWithReload):
    """Handle options for Network Inspector."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            new_options = {**self.config_entry.options, **user_input}
            # Ensure integer types
            for key in (CONF_SCAN_INTERVAL, CONF_CONSIDER_HOME, CONF_PING_COUNT, CONF_PING_TIMEOUT):
                if key in new_options:
                    new_options[key] = int(new_options[key])
            return self.async_create_entry(title="", data=new_options)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=10,
                            max=300,
                            step=5,
                            unit_of_measurement="seconds",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_CONSIDER_HOME,
                        default=self.config_entry.options.get(
                            CONF_CONSIDER_HOME, DEFAULT_CONSIDER_HOME
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=600,
                            step=10,
                            unit_of_measurement="seconds",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_PING_COUNT,
                        default=self.config_entry.options.get(
                            CONF_PING_COUNT, DEFAULT_PING_COUNT
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=10,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_PING_TIMEOUT,
                        default=self.config_entry.options.get(
                            CONF_PING_TIMEOUT, DEFAULT_PING_TIMEOUT
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=10,
                            unit_of_measurement="seconds",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )
