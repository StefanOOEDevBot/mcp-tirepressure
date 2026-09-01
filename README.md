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