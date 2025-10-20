"""Ashkelon Surf Forecast integration for Home Assistant."""
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ashkelon_surf"


async def async_setup(hass, config):
    """Set up the Ashkelon Surf component."""
    _LOGGER.info("Setting up Ashkelon Surf Forecast integration")
    return True


async def async_setup_entry(hass, entry):
    """Set up from a config entry."""
    return True
