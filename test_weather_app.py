"""
Unit Tests — Weather Lookup App
--------------------------------
Run with:
    python -m pytest test_weather_app.py -v
        or
    python -m unittest test_weather_app -v
"""

import unittest
from unittest.mock import patch, MagicMock

from weather_app import (
    geocode_city,
    fetch_weather,
    celsius_to_fahrenheit,
    format_weather_report,
    WMO_CODES,
)


# ── Helper: build a mock requests.Response ────────────────────────────────────

def _mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    mock.raise_for_status = MagicMock()          # does nothing → simulates 200 OK
    return mock


# ── Test: celsius_to_fahrenheit ───────────────────────────────────────────────

class TestCelsiusToFahrenheit(unittest.TestCase):

    def test_freezing_point(self):
        """0 °C should be 32 °F."""
        self.assertEqual(celsius_to_fahrenheit(0), 32.0)

    def test_boiling_point(self):
        """100 °C should be 212 °F."""
        self.assertEqual(celsius_to_fahrenheit(100), 212.0)

    def test_body_temperature(self):
        """37 °C should be 98.6 °F."""
        self.assertAlmostEqual(celsius_to_fahrenheit(37), 98.6, places=1)

    def test_negative_temperature(self):
        """-40 °C should equal -40 °F."""
        self.assertEqual(celsius_to_fahrenheit(-40), -40.0)

    def test_room_temperature(self):
        """25 °C should be 77 °F."""
        self.assertEqual(celsius_to_fahrenheit(25), 77.0)


# ── Test: geocode_city ────────────────────────────────────────────────────────

class TestGeocodeCity(unittest.TestCase):

    @patch("weather_app.requests.get")
    def test_valid_city(self, mock_get):
        """Should return parsed city info for a valid city."""
        mock_get.return_value = _mock_response({
            "results": [{
                "name":      "Manila",
                "country":   "Philippines",
                "latitude":  14.5995,
                "longitude": 120.9842,
                "timezone":  "Asia/Manila",
            }]
        })

        result = geocode_city("Manila")

        self.assertEqual(result["name"],    "Manila")
        self.assertEqual(result["country"], "Philippines")
        self.assertAlmostEqual(result["latitude"],  14.5995, places=3)
        self.assertAlmostEqual(result["longitude"], 120.9842, places=3)
        self.assertEqual(result["timezone"], "Asia/Manila")

    @patch("weather_app.requests.get")
    def test_city_not_found(self, mock_get):
        """Should raise ValueError when API returns no results."""
        mock_get.return_value = _mock_response({"results": []})

        with self.assertRaises(ValueError) as ctx:
            geocode_city("ThisCityDoesNotExistXYZ")

        self.assertIn("not found", str(ctx.exception).lower())

    @patch("weather_app.requests.get")
    def test_empty_results_key(self, mock_get):
        """Should raise ValueError when 'results' key is missing entirely."""
        mock_get.return_value = _mock_response({})

        with self.assertRaises(ValueError):
            geocode_city("SomeCity")

    @patch("weather_app.requests.get")
    def test_network_error(self, mock_get):
        """Should raise ConnectionError on a network failure."""
        import requests as req_lib
        mock_get.side_effect = req_lib.exceptions.ConnectionError

        with self.assertRaises(ConnectionError):
            geocode_city("Manila")

    @patch("weather_app.requests.get")
    def test_timeout_error(self, mock_get):
        """Should raise ConnectionError on a timeout."""
        import requests as req_lib
        mock_get.side_effect = req_lib.exceptions.Timeout

        with self.assertRaises(ConnectionError):
            geocode_city("Tokyo")


# ── Test: fetch_weather ───────────────────────────────────────────────────────

class TestFetchWeather(unittest.TestCase):

    @patch("weather_app.requests.get")
    def test_valid_weather_response(self, mock_get):
        """Should correctly parse all weather fields."""
        mock_get.return_value = _mock_response({
            "current": {
                "temperature_2m":        28.5,
                "apparent_temperature":  30.1,
                "relative_humidity_2m":  75,
                "wind_speed_10m":        12.3,
                "weather_code":          1,
            }
        })

        result = fetch_weather(14.5995, 120.9842, "Asia/Manila")

        self.assertEqual(result["temperature"], 28.5)
        self.assertEqual(result["feels_like"],  30.1)
        self.assertEqual(result["humidity"],    75)
        self.assertEqual(result["wind_speed"],  12.3)
        self.assertEqual(result["weather_code"], 1)
        self.assertEqual(result["description"], "Mainly clear")

    @patch("weather_app.requests.get")
    def test_unknown_weather_code(self, mock_get):
        """Should return 'Unknown condition' for unrecognized weather codes."""
        mock_get.return_value = _mock_response({
            "current": {
                "temperature_2m": 20.0, "apparent_temperature": 19.0,
                "relative_humidity_2m": 50, "wind_speed_10m": 5.0,
                "weather_code": 999,
            }
        })

        result = fetch_weather(0, 0, "UTC")
        self.assertEqual(result["description"], "Unknown condition")

    @patch("weather_app.requests.get")
    def test_network_error(self, mock_get):
        """Should raise ConnectionError on network failure."""
        import requests as req_lib
        mock_get.side_effect = req_lib.exceptions.ConnectionError

        with self.assertRaises(ConnectionError):
            fetch_weather(14.5995, 120.9842, "Asia/Manila")


# ── Test: format_weather_report ───────────────────────────────────────────────

class TestFormatWeatherReport(unittest.TestCase):

    def setUp(self):
        self.city_info = {
            "name":      "Manila",
            "country":   "Philippines",
            "latitude":  14.5995,
            "longitude": 120.9842,
            "timezone":  "Asia/Manila",
        }
        self.weather = {
            "temperature":  29.0,
            "feels_like":   31.0,
            "humidity":     80,
            "wind_speed":   15.0,
            "weather_code": 0,
            "description":  "Clear sky",
        }

    def test_city_name_in_report(self):
        """Report should contain the city and country name."""
        report = format_weather_report(self.city_info, self.weather)
        self.assertIn("Manila", report)
        self.assertIn("Philippines", report)

    def test_description_in_report(self):
        """Report should contain the weather description."""
        report = format_weather_report(self.city_info, self.weather)
        self.assertIn("Clear sky", report)

    def test_fahrenheit_conversion_in_report(self):
        """Report should include Fahrenheit value for 29°C (84.2°F)."""
        report = format_weather_report(self.city_info, self.weather)
        self.assertIn("84.2", report)

    def test_humidity_in_report(self):
        """Humidity value should appear in the report."""
        report = format_weather_report(self.city_info, self.weather)
        self.assertIn("80%", report)

    def test_report_is_string(self):
        """Return type should be a string."""
        report = format_weather_report(self.city_info, self.weather)
        self.assertIsInstance(report, str)


# ── Test: WMO code coverage ───────────────────────────────────────────────────

class TestWMOCodes(unittest.TestCase):

    def test_clear_sky_code(self):
        self.assertEqual(WMO_CODES[0], "Clear sky")

    def test_thunderstorm_code(self):
        self.assertEqual(WMO_CODES[95], "Thunderstorm")

    def test_heavy_rain_code(self):
        self.assertEqual(WMO_CODES[65], "Heavy rain")

    def test_snow_code(self):
        self.assertEqual(WMO_CODES[73], "Moderate snow")


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
