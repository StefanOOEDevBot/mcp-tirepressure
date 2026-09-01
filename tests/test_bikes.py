"""Tests for bike profiles (bikes.py)."""
import pytest

from mcp_tirepressure.bikes import BIKE_PROFILES, get_bike, get_bikes

EXPECTED_BIKES = {
    "bmc-teamachine",
    "merida-big-nine",
    "merida-esixty-8000",
    "rose-gravel-gravel",
    "rose-gravel-road",
}

def test_all_five_profiles_present():
    assert set(BIKE_PROFILES.keys()) == EXPECTED_BIKES

def test_get_bike_returns_correct_profile():
    bmc = get_bike("bmc-teamachine")
    assert bmc.tire_width == 28
    assert bmc.inner_rim_width == 20
    assert bmc.wheel_diameter == 622
    assert bmc.ride_style == "ROAD"
    assert bmc.rim_type == "CROCHET"
    assert bmc.tire_casing == "STANDARD"
    assert bmc.bike_weight == 8.0

def test_get_bike_unknown_raises_value_error():
    with pytest.raises(ValueError, match="Unknown bike"):
        get_bike("nonexistent-bike")

def test_get_bikes_returns_sorted_list_of_dicts():
    bikes = get_bikes()
    assert isinstance(bikes, list)
    assert len(bikes) == 5
    names = [b["name"] for b in bikes]
    assert names == sorted(names)
    assert "tire_width" in bikes[0]

def test_hookless_rims_are_straight_side():
    for name in ("rose-gravel-gravel", "rose-gravel-road"):
        assert get_bike(name).rim_type == "STRAIGHT_SIDE"
