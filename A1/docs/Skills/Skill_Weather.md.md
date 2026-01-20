---
tags: [skill, weather, api, open-meteo]
---

# 🌤️ Skill: Weather (Open-Meteo)

Real-time weather data integration using the **Open-Meteo** free API. No API key required!

## ⚙️ Backend
- **Provider**: [Open-Meteo](https://open-meteo.com)
- **Library**: `requests` (Python)
- **Geocoding**: Built-in location resolution
- **Privacy**: High (No API key, no tracking)
- **Cost**: Free for non-commercial use

## 🔄 API Endpoints

| Endpoint | Purpose |
| :--- | :--- |
| `geocoding-api.open-meteo.com/v1/search` | Location → Coordinates |
| `api.open-meteo.com/v1/forecast` | Weather data |

## 📊 Available Data

### Current Weather
- Temperature (actual & feels-like)
- Humidity percentage
- Wind speed & direction
- Weather conditions (WMO codes)
- Precipitation amount
- Day/Night indicator

### Forecast
- Up to 16 days ahead
- Daily high/low temperatures
- Weather conditions
- Precipitation probability
- Wind speed maximum

## 🎯 Functions

| Function | Description | Example |
| :--- | :--- | :--- |
| `get_weather(location)` | Current conditions | "Weather in Chennai" |
| `get_weather_forecast(location, days)` | Multi-day forecast | "5-day forecast for Tokyo" |
| `is_it_raining(location)` | Rain check | "Is it raining in Mumbai?" |
| `should_i_carry_umbrella(location)` | Smart recommendation | "Should I carry umbrella?" |
| `geocode(location)` | Location lookup | Internal use |

## 🔀 Router Integration

Weather queries are detected via keywords:
- `weather`, `temperature`, `humidity`
- `forecast`, `rain`, `raining`
- `umbrella`, `sunny`, `cloudy`

### Location Extraction Patterns
```regex
weather (?:in|at|for|of) ([location])
([location]) weather
forecast for ([location])
raining in ([location])
```

### Intents
| Intent | Trigger | Handler |
| :--- | :--- | :--- |
| `weather` | "weather in X" | `get_weather()` |
| `weather_forecast` | "forecast for X" | `get_weather_forecast()` |
| `weather_rain` | "rain/umbrella" | `should_i_carry_umbrella()` |

## 📝 Examples

### Current Weather
**User**: "What's the weather in Tokyo?"
**A1**: "In Tokyo, Japan, it's currently 8°C with overcast. It feels like 5°C. Humidity is 65% and wind speed is 12 km/h."

### Forecast
**User**: "3-day forecast for Chennai"
**A1**: "Here's the 3-day forecast for Chennai, India: Monday: 32/25°C, partly cloudy. Tuesday: 31/24°C, mainly clear. Wednesday: 33/26°C, clear sky."

### Umbrella Check
**User**: "Should I carry an umbrella in London?"
**A1**: "Yes, I'd recommend carrying an umbrella. London expects slight rain showers with 2.5mm precipitation today."

## 🌍 Supported Locations

Open-Meteo supports worldwide locations:
- Major cities (Chennai, Tokyo, London, New York)
- Small towns (via geocoding)
- Multiple countries with same city name (disambiguates automatically)

### Default Location
If no location specified, defaults to **Chennai, India** (for Tamil users).

---
## 🕸️ Connections
- Part of [[Skills/Skill_Overview|Skills System]]
- Routes via [[Core/Core_Router|Intent Router]]
- Speaks via [[Core/Core_TTS|TTS Engine]]

[[00_Index|🔙 Return to Index]]
