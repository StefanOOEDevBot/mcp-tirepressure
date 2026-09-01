"""MCP server exposing a SRAM-like tire pressure formula as tools."""
from __future__ import annotations

from mcp.server import MCPServer

from .bikes import get_bike as _get_bike
from .bikes import get_bikes as _get_bikes
from .core import calc_pressure as _calc
from .weather import get_weather as _get_weather
from .weather import is_wet as _is_wet

HOOKLESS_CAP_BAR = 4.96

mcp = MCPServer(
    "mcp-tirepressure",
    version="0.1.0",
    instructions=(
        "Tire pressure calculator implementing a SRAM-like formula. "
        "Values are for guidance only — no warranty. "
        "Always check the tire's max pressure marking. "
        "All pressures are returned in bar. Use get_bikes() to see available "
        "bikes, get_recommended_pressure() for a one-call recommendation with "
        "live weather. Surface values: DRY, WET, SNOW."
    ),
)


def _apply_hookless_cap(front: float, rear: float, rim_type: str) -> tuple[float, float, list[str]]:
    """Cap pressure for hookless rims at 4.96 bar (72 PSI). Returns (front, rear, notes)."""
    notes: list[str] = []
    if rim_type == "STRAIGHT_SIDE":
        if front > HOOKLESS_CAP_BAR:
            front = HOOKLESS_CAP_BAR
            notes.append(f"Hookless-Felge: vorne auf {HOOKLESS_CAP_BAR} bar (72 PSI) begrenzt")
        if rear > HOOKLESS_CAP_BAR:
            rear = HOOKLESS_CAP_BAR
            notes.append(f"Hookless-Felge: hinten auf {HOOKLESS_CAP_BAR} bar (72 PSI) begrenzt")
    return front, rear, notes


@mcp.tool()
def get_bikes() -> list[dict]:
    """List all configured bike profiles (name, tire/rim specs, style)."""
    return _get_bikes()


@mcp.tool()
def get_bike(name: str) -> dict:
    """Get a single bike profile by name. Returns specs + bike weight."""
    profile = _get_bike(name)
    return profile.model_dump()


@mcp.tool()
def calc_pressure(bike: str, rider_weight: float, bike_weight: float,
                  surface: str = "DRY") -> dict:
    """Calculate recommended tire pressure (front/rear in bar) for a given bike,
    rider weight, and surface (DRY/WET/SNOW). Applies hookless rim cap where needed."""
    profile = _get_bike(bike)
    front = _calc(
        rider_weight=rider_weight, bike_weight=bike_weight,
        tire_width=profile.tire_width, inner_rim_width=profile.inner_rim_width,
        wheel_diameter=profile.wheel_diameter, ride_style=profile.ride_style,
        rim_type=profile.rim_type, tire_casing=profile.tire_casing,
        surface=surface, wheel_position="FRONT",
    )
    rear = _calc(
        rider_weight=rider_weight, bike_weight=bike_weight,
        tire_width=profile.tire_width, inner_rim_width=profile.inner_rim_width,
        wheel_diameter=profile.wheel_diameter, ride_style=profile.ride_style,
        rim_type=profile.rim_type, tire_casing=profile.tire_casing,
        surface=surface, wheel_position="REAR",
    )
    front, rear, notes = _apply_hookless_cap(front, rear, profile.rim_type)
    return {
        "bike": profile.name,
        "surface": surface,
        "front_bar": round(front, 2),
        "rear_bar": round(rear, 2),
        "notes": notes,
    }


@mcp.tool()
async def get_recommended_pressure(bike: str, rider_weight: float,
                                    bike_weight: float,
                                    lat: float, lon: float) -> dict:
    """One-call recommended pressure with live weather. Fetches Open-Meteo data,
    determines wet/dry, and returns front/rear pressure in bar."""
    weather = await _get_weather(lat, lon)
    wet, reason = _is_wet(weather)
    surface = "WET" if wet else "DRY"
    profile = _get_bike(bike)
    front = _calc(
        rider_weight=rider_weight, bike_weight=bike_weight,
        tire_width=profile.tire_width, inner_rim_width=profile.inner_rim_width,
        wheel_diameter=profile.wheel_diameter, ride_style=profile.ride_style,
        rim_type=profile.rim_type, tire_casing=profile.tire_casing,
        surface=surface, wheel_position="FRONT",
    )
    rear = _calc(
        rider_weight=rider_weight, bike_weight=bike_weight,
        tire_width=profile.tire_width, inner_rim_width=profile.inner_rim_width,
        wheel_diameter=profile.wheel_diameter, ride_style=profile.ride_style,
        rim_type=profile.rim_type, tire_casing=profile.tire_casing,
        surface=surface, wheel_position="REAR",
    )
    front, rear, notes = _apply_hookless_cap(front, rear, profile.rim_type)
    return {
        "bike": profile.name,
        "surface": surface,
        "weather_reason": reason,
        "front_bar": round(front, 2),
        "rear_bar": round(rear, 2),
        "notes": notes,
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
