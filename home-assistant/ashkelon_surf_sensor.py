"""
Ashkelon Surf Forecast Sensor for Home Assistant
Simple custom component that fetches surf data from 4surfers.co.il API
"""
import logging
import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ashkelon_surf"
SCAN_INTERVAL = timedelta(minutes=30)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)

# Beach configuration
BEACH_AREA_ID = "80"  # Ashkelon
API_URL = "https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Ashkelon surf sensor."""
    _LOGGER.info("Setting up Ashkelon Surf Forecast sensor")
    
    session = async_get_clientsession(hass)
    sensors = [
        AshkelonSurfSensor(session, "today", 0),
        AshkelonSurfSensor(session, "tomorrow", 1),
        AshkelonSurfSensor(session, "day_after", 2),
    ]
    
    async_add_entities(sensors, True)

class AshkelonSurfSensor(Entity):
    """Representation of an Ashkelon surf forecast sensor."""

    def __init__(self, session, name, day_offset):
        """Initialize the sensor."""
        self._session = session
        self._name = f"Ashkelon Surf {name.replace('_', ' ').title()}"
        self._day_offset = day_offset
        self._state = None
        self._attributes = {}
        self._available = True

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"ashkelon_surf_{self._day_offset}"

    @property
    def state(self):
        """Return the state of the sensor (average wave height in feet)."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "ft"

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if self._state is None:
            return "mdi:waves"
        elif float(self._state) < 1.3:
            return "mdi:waves"
        elif float(self._state) < 3.3:
            return "mdi:surfing"
        else:
            return "mdi:alert-circle"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            _LOGGER.debug(f"Updating {self._name}")
            
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json;charset=UTF-8",
                "User-Agent": "HomeAssistant/1.0",
                "Origin": "https://4surfers.co.il",
                "Referer": "https://4surfers.co.il/"
            }
            
            data = {"beachAreaId": BEACH_AREA_ID}
            
            async with async_timeout.timeout(20):
                async with self._session.post(
                    API_URL,
                    json=data,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        _LOGGER.error(f"API returned status {response.status}")
                        self._available = False
                        return
                    
                    result = await response.json()
            
            if not result or "dailyForecastList" not in result:
                _LOGGER.error("No forecast data in API response")
                self._available = False
                return
            
            daily_list = result["dailyForecastList"]
            
            if len(daily_list) <= self._day_offset:
                _LOGGER.error(f"Not enough forecast days for offset {self._day_offset}")
                self._available = False
                return
            
            day_data = daily_list[self._day_offset]
            forecast_hours = day_data.get("forecastHours", [])
            
            # Extract key times
            times = {
                "06:00": None,
                "09:00": None,
                "12:00": None,
                "18:00": None
            }
            
            for hour_data in forecast_hours:
                time_str = hour_data.get("forecastLocalHour", "")
                for target_time in times.keys():
                    if target_time in time_str:
                        times[target_time] = hour_data
                        break
            
            # Calculate average height and collect data
            heights_meters = []
            morning_height = None
            noon_height = None
            evening_height = None
            
            morning_hebrew = "N/A"
            noon_hebrew = "N/A"
            evening_hebrew = "N/A"
            
            if times["06:00"]:
                morning_height = times["06:00"].get("WaveHeight", 0)
                heights_meters.append(morning_height)
                morning_hebrew = times["06:00"].get("surfHeightDesc", "N/A")
            
            if times["12:00"]:
                noon_height = times["12:00"].get("WaveHeight", 0)
                heights_meters.append(noon_height)
                noon_hebrew = times["12:00"].get("surfHeightDesc", "N/A")
            
            if times["18:00"]:
                evening_height = times["18:00"].get("WaveHeight", 0)
                heights_meters.append(evening_height)
                evening_hebrew = times["18:00"].get("surfHeightDesc", "N/A")
            
            # Convert to feet (1m = 3.28084ft)
            def meters_to_feet(m):
                if m is None:
                    return None
                return round(m * 3.28084, 1)
            
            avg_meters = sum(heights_meters) / len(heights_meters) if heights_meters else 0
            avg_feet = meters_to_feet(avg_meters)
            
            # Update state and attributes
            self._state = avg_feet
            self._attributes = {
                "morning_height_ft": meters_to_feet(morning_height),
                "noon_height_ft": meters_to_feet(noon_height),
                "evening_height_ft": meters_to_feet(evening_height),
                "morning_hebrew": morning_hebrew,
                "noon_hebrew": noon_hebrew,
                "evening_hebrew": evening_hebrew,
                "morning_time": "06:00",
                "noon_time": "12:00",
                "evening_time": "18:00",
                "forecast_date": day_data.get("forecastLocalTime", "")[:10],
                "beach": "Ashkelon",
                "beach_hebrew": "אשקלון",
                "unit": "ft"
            }
            
            # Add surf quality assessment
            if avg_feet < 1.3:
                quality = "Poor"
                quality_hebrew = "לא טוב"
            elif avg_feet < 2.6:
                quality = "Fair"
                quality_hebrew = "בסדר"
            elif avg_feet < 4.9:
                quality = "Good"
                quality_hebrew = "טוב"
            else:
                quality = "Excellent"
                quality_hebrew = "מעולה"
            
            self._attributes["surf_quality"] = quality
            self._attributes["surf_quality_hebrew"] = quality_hebrew
            
            self._available = True
            _LOGGER.debug(f"Updated {self._name}: {avg_feet}ft - {quality}")
            
        except Exception as err:
            _LOGGER.error(f"Error updating {self._name}: {err}")
            self._available = False
