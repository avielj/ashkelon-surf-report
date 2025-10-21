"""Home Assistant sensors for the Ashkelon Surf Forecast."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity

DOMAIN = "ashkelon_surf"
_LOGGER = logging.getLogger(__name__)

API_URL = "https://4surfers.co.il/webapi/BeachArea/GetBeachAreaForecast"
BEACH_AREA_ID = "80"
BEACH_NAME_EN = "Ashkelon"
BEACH_NAME_HE = "אשקלון"
SCAN_INTERVAL = timedelta(hours=3)
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=1)
REQUEST_TIMEOUT = 20
TARGET_TIMES: tuple[str, ...] = ("06:00", "09:00", "12:00", "18:00")
STAR_BINS = (0.5, 1.0, 1.5, 2.0, 2.5)


@dataclass
class SurfSession:
    """Structured data for a single time slot."""

    time: str
    height_m: Optional[float]
    height_ft: Optional[float]
    period_s: Optional[float]
    stars: str
    surf_rank: Optional[str]
    hebrew_height: Optional[str]
    wind_kts: Optional[float]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "height_m": self.height_m,
            "height_ft": self.height_ft,
            "period_s": self.period_s,
            "stars": self.stars,
            "surf_rank": self.surf_rank,
            "hebrew_height": self.hebrew_height,
            "wind_kts": self.wind_kts,
        }


@dataclass
class SurfDay:
    """Structured data for a forecast day."""

    label: str
    date_iso: str
    hebrew_day: str
    sessions: List[SurfSession] = field(default_factory=list)
    missing_times: List[str] = field(default_factory=list)
    average_height_m: Optional[float] = None
    average_height_ft: Optional[float] = None
    stars: str = "☆☆☆☆☆"
    best_session: Optional[SurfSession] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "date_iso": self.date_iso,
            "hebrew_day": self.hebrew_day,
            "sessions": [session.as_dict() for session in self.sessions],
            "missing_times": self.missing_times,
            "average_height_m": self.average_height_m,
            "average_height_ft": self.average_height_ft,
            "stars": self.stars,
            "best_session": self.best_session.as_dict() if self.best_session else None,
        }


class SurfForecastData:
    """Shared helper fetching forecast data once per refresh cycle."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._session = async_get_clientsession(hass)
        self._lock = asyncio.Lock()
        self._last_update: Optional[datetime] = None
        self._data: Dict[str, Any] | None = None

    async def async_get_data(self) -> Dict[str, Any] | None:
        async with self._lock:
            now = datetime.utcnow()
            if (
                self._data is not None
                and self._last_update is not None
                and now - self._last_update < MIN_TIME_BETWEEN_UPDATES
            ):
                return self._data

            payload = {"beachAreaId": BEACH_AREA_ID}
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json;charset=UTF-8",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36"
                ),
                "Origin": "https://4surfers.co.il",
                "Referer": "https://4surfers.co.il/",
            }

            try:
                async with asyncio.timeout(REQUEST_TIMEOUT):
                    async with self._session.post(API_URL, json=payload, headers=headers) as response:
                        if response.status != 200:
                            text = await response.text()
                            raise RuntimeError(f"Non-200 response ({response.status}): {text[:128]}")
                        raw = await response.json()
            except asyncio.TimeoutError as exc:
                _LOGGER.error("Timeout fetching Ashkelon surf forecast: %s", exc)
                self._data = None
                self._last_update = now
                return None
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.error("Error fetching Ashkelon surf forecast: %s", exc)
                self._data = None
                self._last_update = now
                return None

            parsed = self._parse_response(raw)
            self._data = {
                "fetched_at": now.isoformat(),
                "days": [day.as_dict() for day in parsed],
            }
            self._last_update = now
            return self._data

    def _parse_response(self, payload: Dict[str, Any]) -> List[SurfDay]:
        days: List[SurfDay] = []
        daily_list = payload.get("dailyForecastList", []) or []
        for day_index, day_data in enumerate(daily_list[:3]):
            forecast_date = _parse_datetime(day_data.get("forecastLocalTime"))
            if forecast_date is None:
                continue

            label = "Today" if day_index == 0 else f"{forecast_date.strftime('%a')} {forecast_date.strftime('%d/%m')}"
            hebrew_day = _get_hebrew_day(forecast_date.weekday())
            surf_day = SurfDay(label=label, date_iso=forecast_date.date().isoformat(), hebrew_day=hebrew_day)

            forecast_hours = day_data.get("forecastHours", []) or []
            available_sessions: List[SurfSession] = []
            missing_times: List[str] = []

            for slot in TARGET_TIMES:
                hour_data = _match_hour_data(forecast_hours, slot)
                if hour_data is None:
                    missing_times.append(slot)
                    continue

                height_m = _extract_height(hour_data)
                height_ft = _meters_to_feet(height_m) if height_m is not None else None
                period = _safe_float(hour_data.get("WavePeriod") or hour_data.get("wavePeriod"))
                surf_rank = hour_data.get("surfRankMark")
                hebrew_height = hour_data.get("surfHeightDesc")
                wind_kts = _safe_float(hour_data.get("WindSpeedInKnots") or hour_data.get("windSpeedInKnots"))
                stars = _height_to_stars(height_m)

                available_sessions.append(
                    SurfSession(
                        time=slot,
                        height_m=height_m,
                        height_ft=height_ft,
                        period_s=period,
                        stars=stars,
                        surf_rank=surf_rank,
                        hebrew_height=hebrew_height,
                        wind_kts=wind_kts,
                    )
                )

            surf_day.sessions = available_sessions
            surf_day.missing_times = missing_times

            if available_sessions:
                heights_m = [session.height_m for session in available_sessions if session.height_m is not None]
                if heights_m:
                    avg_height_m = sum(heights_m) / len(heights_m)
                    surf_day.average_height_m = round(avg_height_m, 3)
                    surf_day.average_height_ft = _meters_to_feet(avg_height_m)
                    surf_day.stars = _height_to_stars(avg_height_m)

                surf_day.best_session = max(
                    (s for s in available_sessions if s.height_m is not None),
                    key=lambda session: session.height_m,
                    default=None,
                )

            days.append(surf_day)

        return days


async def async_setup_platform(hass: HomeAssistant, config: Dict[str, Any], async_add_entities, discovery_info=None) -> None:  # type: ignore[override]
    """Set up surf sensors for Ashkelon."""
    hass.data.setdefault(DOMAIN, {})
    if "data" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["data"] = SurfForecastData(hass)

    data: SurfForecastData = hass.data[DOMAIN]["data"]

    sensors = [
        AshkelonSurfSensor(data, "Ashkelon Surf Today", 0),
        AshkelonSurfSensor(data, "Ashkelon Surf Tomorrow", 1),
        AshkelonSurfSensor(data, "Ashkelon Surf Day After", 2),
    ]

    async_add_entities(sensors, True)


class AshkelonSurfSensor(Entity):
    """Representation of a single-day surf summary sensor."""

    def __init__(self, data: SurfForecastData, name: str, day_offset: int) -> None:
        self._data = data
        self._name = name
        self._day_offset = day_offset
        self._state: Optional[float] = None
        self._attrs: Dict[str, Any] = {}
        self._available = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f"ashkelon_surf_{self._day_offset}"

    @property
    def state(self) -> Optional[float]:
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        return "ft"

    @property
    def icon(self) -> str:
        if self._state is None:
            return "mdi:waves"
        if self._state < 1.5:
            return "mdi:waves"
        if self._state < 3.5:
            return "mdi:surfing"
        return "mdi:weather-tornado"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attrs

    @property
    def available(self) -> bool:
        return self._available

    async def async_update(self) -> None:
        data = await self._data.async_get_data()
        if not data:
            self._available = False
            _LOGGER.debug("No data returned for %s", self._name)
            return

        days: List[Dict[str, Any]] = data.get("days", [])
        if len(days) <= self._day_offset:
            self._available = False
            _LOGGER.debug("Insufficient forecast days for %s", self._name)
            return

        day = days[self._day_offset]
        day_avg_ft = day.get("average_height_ft")
        self._state = day_avg_ft
        self._attrs = {
            "beach": BEACH_NAME_EN,
            "beach_hebrew": BEACH_NAME_HE,
            "forecast_date": day.get("date_iso"),
            "day_label": day.get("label"),
            "hebrew_day": day.get("hebrew_day"),
            "sessions": day.get("sessions"),
            "missing_times": day.get("missing_times"),
            "average_height_ft": day_avg_ft,
            "average_height_m": day.get("average_height_m"),
            "stars": day.get("stars"),
            "best_session": day.get("best_session"),
            "last_refreshed": data.get("fetched_at"),
        }

        self._available = True


def _match_hour_data(forecast_hours: List[Dict[str, Any]], target_time: str) -> Optional[Dict[str, Any]]:
    for hour in forecast_hours:
        slot = str(hour.get("forecastLocalHour", ""))
        if target_time in slot:
            return hour
    return None


def _extract_height(hour_data: Dict[str, Any]) -> Optional[float]:
    surf_from = _safe_float(hour_data.get("SurfHeightFrom") or hour_data.get("surfHeightFrom"))
    surf_to = _safe_float(hour_data.get("SurfHeightTo") or hour_data.get("surfHeightTo"))
    if surf_from is not None and surf_to is not None:
        return round((surf_from + surf_to) / 2, 3)

    wave_height = _safe_float(
        hour_data.get("waveHeight")
        or hour_data.get("WaveHeight")
        or hour_data.get("WaveHeightInMeters")
    )
    return round(wave_height, 3) if wave_height is not None else None


def _height_to_stars(height_m: Optional[float]) -> str:
    if height_m is None:
        return "☆☆☆☆☆"

    thresholds = STAR_BINS
    if height_m <= thresholds[0]:
        return "☆☆☆☆☆"
    if height_m <= thresholds[1]:
        return "⭐☆☆☆☆"
    if height_m <= thresholds[2]:
        return "⭐⭐☆☆☆"
    if height_m <= thresholds[3]:
        return "⭐⭐⭐☆☆"
    if height_m <= thresholds[4]:
        return "⭐⭐⭐⭐☆"
    return "⭐⭐⭐⭐⭐"


def _meters_to_feet(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return round(value * 3.28084, 1)


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    try:
        if isinstance(value, datetime):
            return value
        text = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(text)
    except (TypeError, ValueError):
        _LOGGER.debug("Unable to parse datetime value: %s", value)
        return None


def _get_hebrew_day(index: int) -> str:
    hebrew_days = [
        "א'",
        "ב'",
        "ג'",
        "ד'",
        "ה'",
        "ו'",
        "שבת",
    ]
    if 0 <= index < len(hebrew_days):
        return hebrew_days[index]
    return ""
