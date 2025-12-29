
from __future__ import annotations
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    async_add_entities([
        DoorbellStatusSensor(coordinator),
        #DoorbellInfoSensor(coordinator, "host"),
        #DoorbellInfoSensor(coordinator, "port"),
    ])

class DoorbellStatusSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Status"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "doorbell_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "doorbell")},
            "name": "Doorbell",
            "manufacturer": "luksi1234",
        }

    @property
    def native_value(self):
        # Expected: {"status": "..."} or {"error": "..."}
        status = self.coordinator.data.get("status")
        _LOGGER.debug("sensor: status: %s",status)
        return (status or {}).get("status") or (status or {}).get("error") or "unknown"

class DoorbellInfoSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, key: str):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"Info {key}"
        self._attr_unique_id = f"doorbell_info_{key}"

    @property
    def native_value(self):
        # Expected: {"addon": "...", "port": "..."} or {"error": "..."}
        info = self.coordinator.data.get("info")
        _LOGGER.debug("sensor: info: %s",info)
        return (info.get('info') or {}).get(self._key) or (info or {}).get("error") or "unknown"
