# 🌤 Weather Lookup App

A command-line Python application that retrieves real-time weather data for any city in the world using free, open REST APIs — no API key required.

Built as a team project for **CS / IT — Module 3: REST APIs & Git Collaboration**  
*Mapúa Institute of Technology — Laguna Campus*

---

## 📋 Features

- Search weather by city name (worldwide)
- Displays temperature in **°C and °F**
- Shows: condition description, feels-like temp, humidity, and wind speed
- Human-friendly weather condition descriptions (WMO standard codes)
- Graceful error handling for bad input and network issues
- Full unit test suite (20 tests)

---

## 🔌 APIs Used

| API | Purpose | Docs |
|-----|---------|------|
| [Open-Meteo Geocoding](https://open-meteo.com/en/docs/geocoding-api) | City name → coordinates | Free, no key |
| [Open-Meteo Weather](https://open-meteo.com/en/docs) | Coordinates → weather data | Free, no key |

---

## 🛠 Requirements

- Python **3.8+**
- `requests` library

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-team>/weather-lookup-app.git
cd weather-lookup-app
```

### 2. (Optional) Create a virtual environment

```bash
python -m venv venv

# Activate — Windows:
venv\Scripts\activate

# Activate — macOS / Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the App

```bash
python weather_app.py
```

**Example session:**

```
┌─────────────────────────────────┐
│     🌤  Weather Lookup App       │
└─────────────────────────────────┘

Enter city name (or 'quit' to exit): Manila

  🔍 Looking up 'Manila'...
  📡 Fetching weather for Manila, Philippines...

=============================================
  Weather Report — Manila, Philippines
=============================================
  Condition   : Partly cloudy
  Temperature : 31.2°C  /  88.2°F
  Feels Like  : 38.4°C  /  101.1°F
  Humidity    : 74%
  Wind Speed  : 18.5 km/h
  Timezone    : Asia/Manila
=============================================

Enter city name (or 'quit' to exit): quit

Goodbye! Stay safe out there. 👋
```

---

## 🧪 Running Tests

```bash
# Using pytest (recommended)
pip install pytest
python -m pytest test_weather_app.py -v

# Or using built-in unittest
python -m unittest test_weather_app -v
```

**Test coverage includes:**

| Test Class | What it tests |
|---|---|
| `TestCelsiusToFahrenheit` | Unit conversion edge cases |
| `TestGeocodeCity` | Valid city, not found, network errors, timeouts |
| `TestFetchWeather` | Valid response, unknown code, network error |
| `TestFormatWeatherReport` | Output formatting, type checks |
| `TestWMOCodes` | WMO weather code lookup table |

---

## 📁 Project Structure

```
weather-lookup-app/
├── weather_app.py        # Main application
├── test_weather_app.py   # Unit tests
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 🤝 Git Collaboration Workflow

We followed the **feature branch** workflow:

1. `main` — stable, production-ready code only
2. `dev` — integration branch for completed features
3. Feature branches — one per task (e.g., `feature/geocoding`, `feature/tests`)

### Branching convention

```bash
git checkout -b feature/<your-feature-name>
# ... make changes ...
git add .
git commit -m "feat: describe what you did"
git push origin feature/<your-feature-name>
# Open a Pull Request → merge into dev → merge into main
```

### Commit message format

```
feat:   new feature
fix:    bug fix
test:   adding or updating tests
docs:   README or comment updates
refactor: code cleanup
```

---

## 👥 Team

| Name | Role |
|------|------|
| Adrian Jan Gutierrez | Scrum Leader |
| Danielle Escolano | Recorder |
| Francene Elomina | Developer |
| Karylle Manangkil | Developer |
| Shelley Reyes | Developer |

---

## 📄 License

For academic use only — Mapúa Institute of Technology, Laguna Campus.
