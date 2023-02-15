"""Sensor platform for screenlogic_debug."""
from __future__ import annotations

from screenlogicpy.const import CODE, DATA as SL_DATA

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ScreenLogicDebugDataUpdateCoordinator
from .entity import ScreenLogicDebugEntity


DEBUG_SENSORS = {
    SL_DATA.KEY_CONFIG: [
        "controller_buffer",
        "ok",
    ],
    SL_DATA.KEY_CIRCUITS: [],
    SL_DATA.KEY_PUMPS: [
        "data",
        "state",
    ],
    SL_DATA.KEY_CHEMISTRY: [
        "status",
        "flags",
    ],
    SL_DATA.KEY_SCG: [
        "scg_flags",
    ],
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up entry."""
    entities: list[ScreenLogicDebugSensor] = []
    coordinator: ScreenLogicDebugDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # Debug sensors
    for cat_key, data_keys in DEBUG_SENSORS.items():
        if cat_data := coordinator.gateway_data.get(cat_key):
            if cat_key in {SL_DATA.KEY_CIRCUITS, SL_DATA.KEY_PUMPS}:
                for idx, data_points in cat_data.items():
                    entities.extend(
                        [
                            ScreenLogicDebugSensor(coordinator, data, cat_key, idx)
                            for data in data_points.keys()
                            if str(data) in data_keys
                            or str(data).startswith("unknown_at_offset_")
                        ]
                    )
            else:
                entities.extend(
                    [
                        ScreenLogicDebugSensor(coordinator, data, cat_key)
                        for data in cat_data.keys()
                        if str(data) in data_keys
                        or str(data).startswith("unknown_at_offset_")
                    ]
                )
    for idx_key in ["alerts", "notifications"]:
        entities.append(
            ScreenLogicDebugSensor(coordinator, "_raw", SL_DATA.KEY_CHEMISTRY, idx_key)
        )

    async_add_entities(entities)


class ScreenLogicDebugSensor(ScreenLogicDebugEntity, SensorEntity):
    """Debug Sensor for tracking unknown values."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator, data_key, category, index=None, enabled=True
    ) -> None:
        """Initialize the debug sensor."""
        identifier = (
            f"{category}_{index}_{data_key}"
            if index is not None
            else f"{category}_{data_key}"
        )
        super().__init__(coordinator, identifier, enabled)
        self._key = data_key
        self._category = category
        self._index = index
        self._attr_name = identifier

    @callback
    def _async_data_updated(self) -> None:
        """Handle data updates."""
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        self.async_on_remove(
            await self.gateway.async_subscribe_client(
                self._async_data_updated, CODE.STATUS_CHANGED
            )
        )
        self.async_on_remove(
            await self.gateway.async_subscribe_client(
                self._async_data_updated, CODE.CHEMISTRY_CHANGED
            )
        )

    @property
    def native_value(self):
        """Return the value."""
        return (
            self.gateway_data[self._category][self._index][self._key]
            if self._index is not None
            else self.gateway_data[self._category][self._key]
        )
