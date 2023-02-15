"""BlueprintEntity class"""
from __future__ import annotations

from typing import Any

from screenlogicpy.const import DATA as SL_DATA, EQUIPMENT

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import ScreenLogicDebugDataUpdateCoordinator


class ScreenLogicDebugEntity(CoordinatorEntity[ScreenLogicDebugDataUpdateCoordinator]):
    """Base class for all ScreenLogic entities."""

    def __init__(self, coordinator, data_key, enabled=True):
        """Initialize of the entity."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_entity_registry_enabled_default = enabled
        self._attr_unique_id = f"{self.mac}_{self._data_key}"

        controller_type = self.config_data["controller_type"]
        hardware_type = self.config_data["hardware_type"]
        try:
            equipment_model = EQUIPMENT.CONTROLLER_HARDWARE[controller_type][
                hardware_type
            ]
        except KeyError:
            equipment_model = f"Unknown Model C:{controller_type} H:{hardware_type}"
        self._attr_device_info = DeviceInfo(
            connections={(dr.CONNECTION_NETWORK_MAC, self.mac)},
            manufacturer="Pentair",
            model=equipment_model,
            name=self.gateway_name,
            sw_version=self.gateway.version,
        )

    @property
    def mac(self):
        """Mac address."""
        return self.coordinator.config_entry.unique_id

    @property
    def config_data(self):
        """Shortcut for config data."""
        return self.gateway_data[SL_DATA.KEY_CONFIG]

    @property
    def gateway(self):
        """Return the gateway."""
        return self.coordinator.gateway

    @property
    def gateway_data(self) -> dict[str | int, Any]:
        """Return the gateway data."""
        return self.gateway.get_data()

    @property
    def gateway_name(self):
        """Return the configured name of the gateway."""
        return self.gateway.name

    async def _async_refresh(self):
        """Refresh the data from the gateway."""
        await self.coordinator.async_refresh()
        # Second debounced refresh to catch any secondary
        # changes in the device
        await self.coordinator.async_request_refresh()

    async def _async_refresh_timed(self, now):
        """Refresh from a timed called."""
        await self.coordinator.async_request_refresh()


class ScreenLogicDebugPushEntity(ScreenLogicDebugEntity):
    """Base class for all ScreenLogic push entities."""

    def __init__(self, coordinator, data_key, message_code, enabled=True):
        """Initialize the entity."""
        super().__init__(coordinator, data_key, enabled)
        self._update_message_code = message_code

    @callback
    def _async_data_updated(self) -> None:
        """Handle data updates."""
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""

        self.async_on_remove(
            await self.gateway.async_subscribe_client(
                self._async_data_updated, self._update_message_code
            )
        )
