# mcp-tirepressure

Lokaler MCP-Server (FastMCP, stdio), der die SRAM AXS Reifendruck-Formel
implementiert und als Tools für den Hermes Agent verfügbar macht.

## Setup

```bash
cd ~/src/mcp-tirepressure
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

## Tools

- `get_bikes()` — alle 5 Rad-Profile
- `get_bike(name)` — ein Rad-Profile
- `calc_pressure(bike, rider_weight, bike_weight, surface)` — Druck v/h in bar
- `get_recommended_pressure(bike, rider_weight, bike_weight, lat, lon)` — mit Live-Wetter

## Registrierung in Hermes

```yaml
mcp_servers:
  mcp-tirepressure:
    command: /home/ss/src/mcp-tirepressure/.venv/bin/python
    args: ["-m", "mcp_tirepressure"]
```

## Tool-Referenz

### `get_bikes()`
Listet alle 5 konfigurierten Rad-Profile auf.
Return: `[{name, tire_width, inner_rim_width, wheel_diameter, ride_style, rim_type, tire_casing, bike_weight}, ...]`

### `get_bike(name: str)`
Rückgabe eines einzelnen Rad-Profils.
Args: `name` — Key aus `get_bikes()` (z.B. `"bmc-teamachine"`).
Return: Profile als dict.

### `calc_pressure(bike, rider_weight, bike_weight, surface="DRY")`
Berechnet den empfohlenen Reifendruck (vorne/hinten) in bar.
Args:
- `bike` — Rad-Name
- `rider_weight` — Fahrergewicht in kg
- `bike_weight` — Radgewicht in kg
- `surface` — `"DRY"`, `"WET"` oder `"SNOW"` (default: `"DRY"`)
Return: `{bike, surface, front_bar, rear_bar, notes}`

### `get_recommended_pressure(bike, rider_weight, bike_weight, lat, lon)`
One-Call-Empfehlung mit Live-Wetter (Open-Meteo).
Args:
- `bike`, `rider_weight`, `bike_weight` — wie oben
- `lat`, `lon` — Koordinaten (z.B. Wien: 48.2082, 16.3738)
Return: `{bike, surface, weather_reason, front_bar, rear_bar, notes}`

## Beispiel (CLI)

```bash
.venv/bin/python -c "
from mcp_tirepressure.server import calc_pressure
import json
print(json.dumps(calc_pressure('bmc-teamachine', 93.0, 8.0, 'DRY'), indent=2))
"
```

## Hookless-Obergrenze

Bei `rim_type == STRAIGHT_SIDE` (hookless) wird der Druck auf max.
**4.96 bar (72 PSI)** begrenzt. Eine Note im `notes`-Feld gibt an,
ob die Grenze ausgelöst wurde.