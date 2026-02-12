
from __future__ import annotations
from datetime import timedelta
import asyncio
import logging
from typing import Any, Dict

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DoorbellClient
from .const import DOMAIN, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "button"]

class AuthError(Exception):
    pass

async def async_setup(hass: HomeAssistant, config: Dict[str, Any]) -> bool:
    """Register domain-level services (available even without entries)."""

    async def _handle_call(call: ServiceCall) -> None:
        # Route to the first loaded entry (or use a target param if you support multi-instance)
        if DOMAIN not in hass.data or not hass.data[DOMAIN]:
            raise HomeAssistantError("doorbell is not configured")
        data = next(iter(hass.data[DOMAIN].values()))
        client: DoorbellClient = data["client"]

        _LOGGER.debug("call_data %s", call.data)

        svc = call.service
        try:
            if svc == "tts":
                #resp = await client.tts(call.data["message"], int(call.data["volume"]))
                resp = await client.tts(call.data["message"], int(call.data.get("volume",100)))
            elif svc == "play":
                #resp = await client.play(call.data["filename"], int(call.data["volume"]))
                resp = await client.play(call.data["filename"], int(call.data.get("volume",100)))
            elif svc == "loop":
                #resp = await client.loop(call.data["filename"], int(call.data["volume"]))
                resp = await client.loop(call.data["filename"], int(call.data.get("volume",100)))
            elif svc == "beep":
                #resp = await client.beep(int(call.data["number"]), int(call.data["volume"]))
                resp = await client.beep(int(call.data["number"]), int(call.data.get("volume",100)))
            elif svc == "stop":
                resp = await client.stop()
            else:
                raise HomeAssistantError(f"Unknown service: {svc}")

            if "error" in resp:
                raise HomeAssistantError(resp["error"])
            _LOGGER.debug("doorbell.%s -> %s", svc, resp)

        except HomeAssistantError:
            raise
        except Exception as err:
            _LOGGER.exception("Service %s failed: %s", svc, err)
            raise HomeAssistantError(str(err)) from err

    # Register services (async in async_setup)
    hass.services.async_register(
        DOMAIN, "tts", _handle_call
    )
    hass.services.async_register(
        DOMAIN, "play", _handle_call
    )
    hass.services.async_register(
        DOMAIN, "loop", _handle_call
    )
    hass.services.async_register(
        DOMAIN, "beep", _handle_call
    )
    hass.services.async_register(
        DOMAIN, "stop", _handle_call
    )
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    base_url = entry.data["base_url"]
    token = entry.data.get("token")
    client = DoorbellClient(hass, base_url, token)

    async def _fetch():
        """Poll status and info together."""
        try:
            status_task = asyncio.create_task(client.status())
            info_task = asyncio.create_task(client.info())
            status, info = await asyncio.gather(status_task, info_task)
            #status = await asyncio.gather(status_task)
            _LOGGER.debug("status_task %s", status)
            _LOGGER.debug("info_task %s", info)



            # If your API returns {"error": "..."} on failure, convert to UpdateFailed
            for name, resp in (("status", status), ("info", info)):
            #for name, resp in (("status", status),):
                if isinstance(resp, dict) and "error" in resp:
                    raise UpdateFailed(f"{name} error: {resp['error']}")

            return {"status": status, "info": info}
            #return {"status": status}


        except AuthError as err:  # If you define/raise a custom auth error
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(f"API error: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="doorbell",
        update_method=_fetch,
        update_interval=timedelta(seconds=10),  # adjust to taste
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
