"""
Weather Lookup App
------------------
Fetches current weather data for any city using:
  - Open-Meteo Geocoding API (no key required)
  - Open-Meteo Weather API    (no key required)

Usage:
    python weather_app.py
"""

import requests
import sys


# ── API endpoints ──────────────────────────────────────────────────────────────
GEO_URL     = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather-code descriptions
WMO_CODES = {
    0:  "Clear sky",
    1:  "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",     
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain", 
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",  
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight showers",
    81: "Moderate showers",
    82: "Violent showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm w/ slight hail",
    99: "Thunderstorm w/ heavy hail",
}


# ── Core functions ─────────────────────────────────────────────────────────────

def geocode_city(city_name: str) -> dict:
    """
    Return the first geocoding result for *city_name*.

    Returns a dict with keys: name, country, latitude, longitude, timezone
    Raises ValueError if the city is not found.
    Raises ConnectionError on network / API failures.
    """
    try:
        response = requests.get(
            GEO_URL,
            params={"name": city_name, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not reach the geocoding API. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise ConnectionError("The geocoding API request timed out.")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(f"Geocoding API returned an error: {e}")

    data = response.json()
    results = data.get("results")

    if not results:
        raise ValueError(f"City '{city_name}' not found. Please try a different name.")

    r = results[0]
    return {
        "name":      r.get("name", city_name),
        "country":   r.get("country", "Unknown"),
        "latitude":  r["latitude"],
        "longitude": r["longitude"],
        "timezone":  r.get("timezone", "UTC"),
    }


def fetch_weather(latitude: float, longitude: float, timezone: str) -> dict:
    """
    Fetch current weather for the given coordinates.

    Returns a dict with keys:
        temperature (°C), feels_like (°C), humidity (%), wind_speed (km/h),
        weather_code (int), description (str)
    Raises ConnectionError on network / API failures.
    """
    params = {
        "latitude":              latitude,
        "longitude":             longitude,
        "current":               [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "wind_speed_10m",
            "weather_code",
        ],
        "timezone":              timezone,
        "wind_speed_unit":       "kmh",
        "temperature_unit":      "celsius",
    }

    try:
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not reach the weather API. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise ConnectionError("The weather API request timed out.")
    except requests.exceptions.HTTPError as e:
        raise ConnectionError(f"Weather API returned an error: {e}")

    current = response.json().get("current", {})
    code    = current.get("weather_code", -1)

    return {
        "temperature": current.get("temperature_2m"),
        "feels_like":  current.get("apparent_temperature"),
        "humidity":    current.get("relative_humidity_2m"),
        "wind_speed":  current.get("wind_speed_10m"),
        "weather_code": code,
        "description": WMO_CODES.get(code, "Unknown condition"),
    }


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return round(celsius * 9 / 5 + 32, 1)


def format_weather_report(city_info: dict, weather: dict) -> str:
    """Build and return a nicely formatted weather report string."""
    temp_c  = weather["temperature"]
    feel_c  = weather["feels_like"]
    temp_f  = celsius_to_fahrenheit(temp_c)
    feel_f  = celsius_to_fahrenheit(feel_c)

    lines = [
        "",
        "=" * 45,
        f"  Weather Report — {city_info['name']}, {city_info['country']}",
        "=" * 45,
        f"  Condition   : {weather['description']}",
        f"  Temperature : {temp_c}°C  /  {temp_f}°F",
        f"  Feels Like  : {feel_c}°C  /  {feel_f}°F",
        f"  Humidity    : {weather['humidity']}%",
        f"  Wind Speed  : {weather['wind_speed']} km/h",
        f"  Timezone    : {city_info['timezone']}",
        "=" * 45,
        "",
    ]
    return "\n".join(lines)


# ── CLI entry point ────────────────────────────────────────────────────────────

def main():
    print("\n┌─────────────────────────────────┐")
    print("│     🌤  Weather Lookup App       │")
    print("└─────────────────────────────────┘")

    while True:
        city_input = input("\nEnter city name (or 'quit' to exit): ").strip()

        if city_input.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! Stay safe out there. 👋\n")
            sys.exit(0)

        if not city_input:
            print("  ⚠  Please enter a city name.")
            continue

        try:
            print(f"\n  🔍 Looking up '{city_input}'...")
            city_info = geocode_city(city_input)

            print(f"  📡 Fetching weather for {city_info['name']}, {city_info['country']}...")
            weather = fetch_weather(
                city_info["latitude"],
                city_info["longitude"],
                city_info["timezone"],
            )

            print(format_weather_report(city_info, weather))

        except ValueError as e:
            print(f"\n  ❌ Error: {e}")
        except ConnectionError as e:
            print(f"\n  ❌ Network Error: {e}")
        except Exception as e:
            print(f"\n  ❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
