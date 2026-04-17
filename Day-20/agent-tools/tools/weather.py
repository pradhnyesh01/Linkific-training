"""
tools/weather.py
Tool 5 – Weather

Gets current weather for any city using the Open-Meteo API.
Free, no API key required, no third-party libraries (stdlib urllib only).

Flow:
  execute(args)
      → get_weather(city, units)
          → _geocode(city)           # Open-Meteo geocoding API
          → Open-Meteo forecast API  # current conditions
          → parse WMO weather code
      → {"success": True/False, ...}
"""

import json
import urllib.request
import urllib.parse
from typing import Any


# ── WMO weather code → human-readable description ────────────────────────────

WMO_CODES: dict[int, str] = {
    0:  "Clear sky",
    1:  "Mainly clear",
    2:  "Partly cloudy",
    3:  "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


# ── Helper: geocode a city name ───────────────────────────────────────────────

def _geocode(city: str) -> dict | None:
    """
    Call Open-Meteo geocoding API. Returns {lat, lon, name, country} or None.
    """
    url = (
        "https://geocoding-api.open-meteo.com/v1/search?"
        + urllib.parse.urlencode({"name": city, "count": 1, "language": "en", "format": "json"})
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        results = data.get("results", [])
        if not results:
            return None
        r = results[0]
        return {
            "lat":     r["latitude"],
            "lon":     r["longitude"],
            "name":    r.get("name", city),
            "country": r.get("country", ""),
        }
    except Exception:
        return None


# ── Core function ─────────────────────────────────────────────────────────────

def get_weather(city: str, units: str = "celsius") -> dict[str, Any]:
    """
    Fetch current weather for a city.

    Args:
        city  : city name (e.g. "London", "Mumbai", "New York")
        units : "celsius" or "fahrenheit"

    Returns:
        {"success": True,  "city": str, "temperature": float, "condition": str, ...}
        {"success": False, "error": str}
    """
    if not city or not city.strip():
        return {"success": False, "error": "City name cannot be empty."}

    units = units.strip().lower()
    if units not in ("celsius", "fahrenheit"):
        units = "celsius"
    temp_unit_param = "fahrenheit" if units == "fahrenheit" else "celsius"
    temp_unit_label = "°F" if units == "fahrenheit" else "°C"

    # Step 1: geocode
    geo = _geocode(city.strip())
    if geo is None:
        return {"success": False, "error": f"City not found: '{city}'. Try a more specific name."}

    # Step 2: fetch current weather
    params = urllib.parse.urlencode({
        "latitude":              geo["lat"],
        "longitude":             geo["lon"],
        "current":               "temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode",
        "temperature_unit":      temp_unit_param,
        "wind_speed_unit":       "kmh",
        "timezone":              "auto",
    })
    url = f"https://api.open-meteo.com/v1/forecast?{params}"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        return {"success": False, "error": f"Weather API error: {e}"}

    current = data.get("current", {})
    wmo_code  = current.get("weathercode", -1)
    condition = WMO_CODES.get(wmo_code, f"WMO code {wmo_code}")

    return {
        "success":          True,
        "city":             geo["name"],
        "country":          geo["country"],
        "latitude":         geo["lat"],
        "longitude":        geo["lon"],
        "temperature":      current.get("temperature_2m"),
        "temperature_unit": temp_unit_label,
        "humidity_percent": current.get("relative_humidity_2m"),
        "wind_speed_kmh":   current.get("wind_speed_10m"),
        "condition":        condition,
        "wmo_code":         wmo_code,
    }



def execute(args: dict) -> dict:
    return get_weather(
        city  = args.get("city", ""),
        units = args.get("units", "celsius"),
    )



if __name__ == "__main__":
    import json as _json

    cities = [
        {"city": "London"},
        {"city": "Mumbai",    "units": "celsius"},
        {"city": "New York",  "units": "fahrenheit"},
        {"city": "Xyzabc123city"},   # error case: non-existent city
    ]

    for t in cities:
        result = execute(t)
        if result["success"]:
            print(f"{result['city']}, {result['country']}: "
                  f"{result['temperature']}{result['temperature_unit']}  "
                  f"💧{result['humidity_percent']}%  "
                  f"💨{result['wind_speed_kmh']} km/h  "
                  f"🌤 {result['condition']}")
        else:
            print(f"Error: {result['error']}")
