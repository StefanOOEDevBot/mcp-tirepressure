"""Tests for MCP tool definitions and integration (server.py)."""
import pytest
import respx
import httpx

from mcp_tirepressure.server import (
    get_bikes, get_bike, calc_pressure, get_recommended_pressure,
)
from mcp_tirepressure.weather import is_wet

# --- get_bikes / get_bike (thin wrappers over bikes.py) ---

def test_get_bikes_tool_returns_5():
    bikes = get_bikes()
    assert len(bikes) == 5
    assert all("name" in b for b in bikes)

def test_get_bike_tool_returns_dict():
    result = get_bike("bmc-teamachine")
    assert result["name"] == "bmc-teamachine"
    assert result["tire_width"] == 28

def test_get_bike_tool_unknown_raises():
    with pytest.raises(ValueError):
        get_bike("does-not-exist")

# --- calc_pressure (tool wrapper) ---

def test_calc_pressure_tool_bmc_dry():
    result = calc_pressure(
        bike="bmc-teamachine", rider_weight=93.0,
        bike_weight=10.0, surface="DRY",
    )
    assert "front_bar" in result
    assert "rear_bar" in result
    assert result["front_bar"] == pytest.approx(4.94, abs=0.01)
    assert result["rear_bar"] == pytest.approx(5.26, abs=0.01)
    assert result["notes"] == []

def test_calc_pressure_tool_wet():
    result = calc_pressure(
        bike="bmc-teamachine", rider_weight=93.0,
        bike_weight=10.0, surface="WET",
    )
    dry = calc_pressure(
        bike="bmc-teamachine", rider_weight=93.0,
        bike_weight=10.0, surface="DRY",
    )
    assert result["front_bar"] == pytest.approx(dry["front_bar"] * 0.9, abs=0.01)

# --- Hookless cap: Rose Gravel (STRAIGHT_SIDE) must not exceed 4.96 bar ---

def test_calc_pressure_tool_hookless_capped():
    result = calc_pressure(
        bike="rose-gravel-road", rider_weight=142.0,
        bike_weight=9.5, surface="DRY",
    )
    assert result["front_bar"] <= 4.96
    assert result["rear_bar"] <= 4.96
    assert any("4.96" in n or "hookless" in n.lower() for n in result["notes"])

def test_calc_pressure_tool_hooked_not_capped():
    """BMC (CROCHET) should NOT be capped at 4.96 even at high weight."""
    result = calc_pressure(
        bike="bmc-teamachine", rider_weight=105.0,
        bike_weight=10.0, surface="DRY",
    )
    # At 105 kg the uncapped value may exceed 4.96 — no cap applied
    assert "hookless" not in " ".join(result["notes"]).lower()

# --- get_recommended_pressure: mocked weather integration ---

@pytest.mark.anyio
@respx.mock
async def test_get_recommended_pressure_dry():
    payload = {
        "current": {"precipitation": 0.0, "weather_code": 0, "temperature_2m": 20.0},
        "hourly": [
            {"precipitation_probability": 10, "weather_code": 0},
            {"precipitation_probability": 10, "weather_code": 0},
        ],
    }
    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json=payload)
    )
    result = await get_recommended_pressure(
        bike="bmc-teamachine", rider_weight=93.0,
        bike_weight=10.0, lat=48.2082, lon=16.3738,
    )
    assert result["surface"] == "DRY"
    assert result["front_bar"] == pytest.approx(4.94, abs=0.01)

@pytest.mark.anyio
@respx.mock
async def test_get_recommended_pressure_wet():
    payload = {
        "current": {"precipitation": 0.5, "weather_code": 61, "temperature_2m": 12.0},
        "hourly": [
            {"precipitation_probability": 80, "weather_code": 61},
            {"precipitation_probability": 70, "weather_code": 63},
        ],
    }
    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json=payload)
    )
    result = await get_recommended_pressure(
        bike="bmc-teamachine", rider_weight=93.0,
        bike_weight=10.0, lat=48.2082, lon=16.3738,
    )
    assert result["surface"] == "WET"
    assert "0.5" in result["weather_reason"]