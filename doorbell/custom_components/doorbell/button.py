
from __future__ import annotations
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        StopButton(data["coordinator"], data["client"]),
        TestPlayButton(data["coordinator"], data["client"]),
        TestTtsButton(data["coordinator"], data["client"]),
        TestBeepButton(data["coordinator"], data["client"])
        ])

class StopButton(CoordinatorEntity, ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Stop"
    _attr_unique_id = "doorbell_stop"

    def __init__(self, coordinator, client):
        super().__init__(coordinator)
        self._client = client
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "doorbell")},
            "name": "Doorbell",
            "manufacturer": "luksi1234",
        }

    async def async_press(self) -> None:
        await self._client.stop()   # GET /stop


class TestPlayButton(CoordinatorEntity, ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Test Play"
    _attr_unique_id = "doorbell_test_play"

    def __init__(self, coordinator, client):
        super().__init__(coordinator)
        self._client = client
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "doorbell")},
            "name": "Doorbell",
            "manufacturer": "luksi1234",
        }

    async def async_press(self) -> None:
        await self._client.play(filename="dingdong.mp3")   # GET /stop


class TestTtsButton(CoordinatorEntity, ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Test Tts"
    _attr_unique_id = "doorbell_test_tts"

    def __init__(self, coordinator, client):
        super().__init__(coordinator)
        self._client = client
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "doorbell")},
            "name": "Doorbell",
            "manufacturer": "luksi1234",
        }

    async def async_press(self) -> None:
        await self._client.tts(message="This is a Test!", lang="en-US")   # GET /stop


class TestBeepButton(CoordinatorEntity, ButtonEntity):
    _attr_has_entity_name = True
    _attr_name = "Test Beep"
    _attr_unique_id = "doorbell_test_beep"

    def __init__(self, coordinator, client):
        super().__init__(coordinator)
        self._client = client
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "doorbell")},
            "name": "Doorbell",
            "manufacturer": "luksi1234",
        }

    async def async_press(self) -> None:
        await self._client.beep(number=2)   # GET /stop
