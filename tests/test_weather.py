"""Tests for weather module (weather.py)."""
import httpx
import pytest
import respx

from mcp_tirepressure.weather import get_weather, is_wet

# --- is_wet: pure logic tests (no network) ---

def _base_data(**overrides):
    d = {
        "current": {"precipitation": 0.0, "weather_code": 0, "temperature_2m": 15.0},
        "hourly": [
            {"precipitation_probability": 10, "weather_code": 0},
            {"precipitation_probability": 10, "weather_code": 0},
            {"precipitation_probability": 10, "weather_code": 0},  # 3rd hour (excluded)
        ],
    }
    d["current"].update(overrides.get("current", {}))
    return d

def test_dry_when_no_precipitation():
    wet, reason = is_wet(_base_data())
    assert wet is False
    assert "Trocken" in reason

def test_wet_when_precipitation_above_threshold():
    data = _base_data(current={"precipitation": 0.2})
    wet, reason = is_wet(data)
    assert wet is True
    assert "0.2" in reason

def test_dry_when_precipitation_at_boundary():
    data = _base_data(current={"precipitation": 0.1})
    wet, _ = is_wet(data)
    assert wet is False  # > 0.1, not >=

def test_wet_when_rain_weather_code():
    data = _base_data(current={"weather_code": 63})  # Drizzle
    wet, reason = is_wet(data)
    assert wet is True
    assert "63" in reason

def test_wet_when_snow_weather_code():
    data = _base_data(current={"weather_code": 71})  # Light snow
    wet, _ = is_wet(data)
    assert wet is True

def test_wet_when_probability_above_50_in_next_2h():
    data = _base_data()
    data["hourly"][1]["precipitation_probability"] = 60  # 2nd hour
    wet, reason = is_wet(data)
    assert wet is True
    assert "60" in reason

def test_dry_when_probability_only_in_third_hour():
    data = _base_data()
    data["hourly"][2]["precipitation_probability"] = 90  # 3rd hour (excluded)
    wet, _ = is_wet(data)
    assert wet is False

# --- get_weather: respx-mocked HTTP tests ---

MOCK_URL = "https://api.open-meteo.com/v1/forecast"

@pytest.mark.anyio
@respx.mock
async def test_get_weather_returns_parsed_json():
    payload = {
        "current": {"precipitation": 0.0, "weather_code": 1, "temperature_2m": 20.0},
        "hourly": [
            {"precipitation_probability": 0, "weather_code": 1},
            {"precipitation_probability": 0, "weather_code": 1},
        ],
    }
    route = respx.get(MOCK_URL).mock(return_value=httpx.Response(200, json=payload))
    result = await get_weather(48.2082, 16.3738)
    assert route.called
    assert result["current"]["weather_code"] == 1
    assert "hourly" in result

@pytest.mark.anyio
@respx.mock
async def test_get_weather_raises_on_http_error():
    respx.get(MOCK_URL).mock(return_value=httpx.Response(503))
    with pytest.raises(httpx.HTTPStatusError):
        await get_weather(48.2082, 16.3738)
