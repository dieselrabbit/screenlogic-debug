"""
Custom integration to track unknown ScreenLogic data with Home Assistant.

For more details about this integration, please refer to
https://github.com/dieselrabbit/screenlogic-debug
"""
from __future__ import annotations

import asyncio
import logging

from screenlogicpy import ScreenLogicError, ScreenLogicGateway

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import async_get_connect_info, ScreenLogicDebugDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    gateway = ScreenLogicGateway()

    connect_info = await async_get_connect_info(hass, entry)

    try:
        await gateway.async_connect(**connect_info)
    except ScreenLogicError as ex:
        _LOGGER.error("Error while connecting to the gateway %s: %s", connect_info, ex)
        raise ConfigEntryNotReady from ex

    coordinator = ScreenLogicDebugDataUpdateCoordinator(
        hass, config_entry=entry, gateway=gateway
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator: ScreenLogicDebugDataUpdateCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.gateway.async_disconnect()

    return unloaded


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
