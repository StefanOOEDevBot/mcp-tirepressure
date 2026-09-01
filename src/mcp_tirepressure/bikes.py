"""Bike profiles for the mcp-tirepressure server."""
from __future__ import annotations

from pydantic import BaseModel


class BikeProfile(BaseModel):
    name: str
    tire_width: int
    inner_rim_width: int
    wheel_diameter: int
    ride_style: str
    rim_type: str
    tire_casing: str
    bike_weight: float


BIKE_PROFILES: dict[str, BikeProfile] = {
    "bmc-teamachine": BikeProfile(
        name="bmc-teamachine", tire_width=28, inner_rim_width=20,
        wheel_diameter=622, ride_style="ROAD", rim_type="CROCHET",
        tire_casing="STANDARD", bike_weight=8.0,
    ),
    "merida-big-nine": BikeProfile(
        name="merida-big-nine", tire_width=54, inner_rim_width=25,
        wheel_diameter=622, ride_style="XC_MTB", rim_type="TUBES",
        tire_casing="STANDARD", bike_weight=14.0,
    ),
    "merida-esixty-8000": BikeProfile(
        name="merida-esixty-8000", tire_width=60, inner_rim_width=29,
        wheel_diameter=622, ride_style="TRAIL_MTB", rim_type="TUBES",
        tire_casing="DOUBLE", bike_weight=26.0,
    ),
    "rose-gravel-gravel": BikeProfile(
        name="rose-gravel-gravel", tire_width=40, inner_rim_width=23,
        wheel_diameter=622, ride_style="GRAVEL", rim_type="STRAIGHT_SIDE",
        tire_casing="STANDARD", bike_weight=9.5,
    ),
    "rose-gravel-road": BikeProfile(
        name="rose-gravel-road", tire_width=32, inner_rim_width=23,
        wheel_diameter=622, ride_style="ROAD", rim_type="STRAIGHT_SIDE",
        tire_casing="STANDARD", bike_weight=9.5,
    ),
}


def get_bikes() -> list[dict]:
    """Return all bike profiles as dicts, sorted by name."""
    return [p.model_dump() for p in sorted(BIKE_PROFILES.values(), key=lambda b: b.name)]


def get_bike(name: str) -> BikeProfile:
    """Return a single bike profile by name. Raises ValueError if unknown."""
    if name not in BIKE_PROFILES:
        known = ", ".join(sorted(BIKE_PROFILES))
        raise ValueError(f"Unknown bike '{name}'. Available: {known}")
    return BIKE_PROFILES[name]
