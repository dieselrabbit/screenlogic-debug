"""DataUpdateCoordinator for screenlogic_debug."""
from __future__ import annotations
from datetime import timedelta
import logging
from typing import Any

from screenlogicpy import ScreenLogicGateway
from screenlogicpy.const import (
    DATA as SL_DATA,
    EQUIPMENT,
    ScreenLogicError,
    ScreenLogicWarning,
    SL_GATEWAY_IP,
    SL_GATEWAY_NAME,
    SL_GATEWAY_PORT,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .config_flow import async_discover_gateways_by_unique_id, name_for_mac
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_get_connect_info(hass: HomeAssistant, entry: ConfigEntry):
    """Construct connect_info from configuration entry and returns it to caller."""
    mac = entry.unique_id
    # Attempt to rediscover gateway to follow IP changes
    discovered_gateways = await async_discover_gateways_by_unique_id(hass)
    if mac in discovered_gateways:
        connect_info = discovered_gateways[mac]
    else:
        _LOGGER.warning("Gateway rediscovery failed")
        # Static connection defined or fallback from discovery
        connect_info = {
            SL_GATEWAY_NAME: name_for_mac(mac),
            SL_GATEWAY_IP: entry.data[CONF_IP_ADDRESS],
            SL_GATEWAY_PORT: entry.data[CONF_PORT],
        }

    return connect_info


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class ScreenLogicDebugDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        gateway: ScreenLogicGateway,
    ) -> None:
        """Initialize."""
        self.config_entry = config_entry
        self.gateway = gateway

        interval = timedelta(
            seconds=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=interval)

    @property
    def gateway_data(self) -> dict[str | int, Any]:
        """Return the gateway data."""
        return self.gateway.get_data()

    async def _async_update_configured_data(self):
        """Update data sets based on equipment config."""
        equipment_flags = self.gateway.get_data()[SL_DATA.KEY_CONFIG]["equipment_flags"]
        if not self.gateway.is_client:
            await self.gateway.async_get_status()
            if equipment_flags & EQUIPMENT.FLAG_INTELLICHEM:
                await self.gateway.async_get_chemistry()

        await self.gateway.async_get_pumps()
        if equipment_flags & EQUIPMENT.FLAG_CHLORINATOR:
            await self.gateway.async_get_scg()

    async def _async_update_data(self):
        """Fetch data from the Screenlogic gateway."""
        try:
            await self._async_update_configured_data()
        except ScreenLogicError as error:
            _LOGGER.warning("Update error - attempting reconnect: %s", error)
            await self._async_reconnect_update_data()
        except ScreenLogicWarning as warn:
            raise UpdateFailed(f"Incomplete update: {warn}") from warn

        return None

    async def _async_reconnect_update_data(self):
        """Attempt to reconnect to the gateway and fetch data."""
        try:
            # Clean up the previous connection as we're about to create a new one
            await self.gateway.async_disconnect()

            connect_info = await async_get_connect_info(self.hass, self.config_entry)
            await self.gateway.async_connect(**connect_info)

            await self._async_update_configured_data()

        except (ScreenLogicError, ScreenLogicWarning) as ex:
            raise UpdateFailed(ex) from ex
