"""Ashkelon Surf Forecast integration for Home Assistant."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "ashkelon_surf"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Ashkelon Surf integration via YAML."""
    # The sensor platform will be loaded automatically via discovery
    return True
