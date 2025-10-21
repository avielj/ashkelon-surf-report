"""Ashkelon Surf Forecast integration for Home Assistant."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "ashkelon_surf"
PLATFORMS: list[str] = ["sensor"]


def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Ashkelon Surf integration via YAML."""
    hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, config)
    return True


def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ashkelon Surf from a config entry."""
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return hass.config_entries.async_unload_platforms(entry, PLATFORMS)
