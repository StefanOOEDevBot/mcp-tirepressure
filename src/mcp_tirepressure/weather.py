"""Open-Meteo weather fetch + wet/dry determination for tire pressure."""
from __future__ import annotations

import httpx

_API_BASE = "https://api.open-meteo.com/v1/forecast"
_WET_CODES = frozenset({61, 63, 65, 66, 67, 71, 73, 75, 77, 80, 81, 82, 85, 86})
_PRECIP_THRESHOLD_MM = 0.1
_PROB_THRESHOLD_PCT = 50
_LOOKAHEAD_HOURS = 2


async def get_weather(lat: float, lon: float) -> dict:
    """Fetch current + hourly weather from Open-Meteo (keyless)."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,precipitation,weather_code",
        "hourly": "precipitation,precipitation_probability,weather_code",
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(_API_BASE, params=params)
        resp.raise_for_status()
        return resp.json()


def is_wet(data: dict) -> tuple[bool, str]:
    """Determine wet/dry surface from Open-Meteo response.

    Wet when: current precipitation > 0.1 mm/h, OR current WMO code indicates
    precipitation, OR precipitation probability > 50% in the next 2 hours.
    Returns (is_wet, reason).
    """
    current = data.get("current", {})
    precip = current.get("precipitation", 0.0)
    code = current.get("weather_code", 0)

    if precip > _PRECIP_THRESHOLD_MM:
        return True, f"Regen aktuell: {precip} mm/h"
    if code in _WET_CODES:
        return True, f"WMO Code {code} = Niederschlag"

    hourly = data.get("hourly", [])
    for entry in hourly[:_LOOKAHEAD_HOURS]:
        prob = entry.get("precipitation_probability") if isinstance(entry, dict) else entry
        if prob is not None and prob > _PROB_THRESHOLD_PCT:
            return True, f"Regenwahrscheinlichkeit {prob}% in den nächsten 2h"

    return False, "Trocken"