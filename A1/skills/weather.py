"""
Open-Meteo Weather Integration for A1 Voice Assistant
Free weather API - No API key required!
https://open-meteo.com/
"""

import requests
from datetime import datetime
from colorama import Fore, Style

# Open-Meteo API endpoints
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Weather code descriptions (WMO codes)
WEATHER_CODES = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}


def geocode(location: str) -> dict | None:
    """
    Convert location name to coordinates using Open-Meteo Geocoding API.
    Returns: {name, latitude, longitude, country} or None
    """
    try:
        params = {
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return {
                "name": result.get("name", location),
                "latitude": result["latitude"],
                "longitude": result["longitude"],
                "country": result.get("country", ""),
                "timezone": result.get("timezone", "auto")
            }
        return None
    except Exception as e:
        print(f"{Fore.RED}[WEATHER] Geocoding error: {e}{Style.RESET_ALL}")
        return None


def get_current_weather(latitude: float, longitude: float, timezone: str = "auto") -> dict | None:
    """
    Get current weather conditions from Open-Meteo.
    """
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "is_day",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m"
            ],
            "timezone": timezone
        }
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "current" in data:
            current = data["current"]
            units = data.get("current_units", {})
            return {
                "temperature": current.get("temperature_2m"),
                "temperature_unit": units.get("temperature_2m", "°C"),
                "feels_like": current.get("apparent_temperature"),
                "humidity": current.get("relative_humidity_2m"),
                "weather_code": current.get("weather_code", 0),
                "weather_description": WEATHER_CODES.get(current.get("weather_code", 0), "unknown"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_unit": units.get("wind_speed_10m", "km/h"),
                "wind_direction": current.get("wind_direction_10m"),
                "is_day": current.get("is_day", 1) == 1,
                "precipitation": current.get("precipitation", 0)
            }
        return None
    except Exception as e:
        print(f"{Fore.RED}[WEATHER] API error: {e}{Style.RESET_ALL}")
        return None


def get_forecast(latitude: float, longitude: float, days: int = 3, timezone: str = "auto") -> list | None:
    """
    Get weather forecast from Open-Meteo.
    """
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "weather_code",
                "precipitation_sum",
                "wind_speed_10m_max"
            ],
            "timezone": timezone,
            "forecast_days": min(days, 16)  # Max 16 days
        }
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "daily" in data:
            daily = data["daily"]
            forecasts = []
            for i in range(len(daily.get("time", []))):
                forecasts.append({
                    "date": daily["time"][i],
                    "temp_max": daily["temperature_2m_max"][i],
                    "temp_min": daily["temperature_2m_min"][i],
                    "weather_code": daily["weather_code"][i],
                    "weather_description": WEATHER_CODES.get(daily["weather_code"][i], "unknown"),
                    "precipitation": daily["precipitation_sum"][i],
                    "wind_max": daily["wind_speed_10m_max"][i]
                })
            return forecasts
        return None
    except Exception as e:
        print(f"{Fore.RED}[WEATHER] Forecast error: {e}{Style.RESET_ALL}")
        return None


def get_weather(location: str = None) -> str:
    """
    Main function to get weather for a location.
    If no location provided, uses a default (Chennai, India for Tamil users).
    Returns a natural language response.
    """
    # Default location if none specified
    if not location or location.strip() == "":
        location = "Chennai"  # Default for Tamil Nadu
    
    print(f"{Fore.CYAN}[WEATHER] Getting weather for: {location}{Style.RESET_ALL}")
    
    # 1. Geocode the location
    geo = geocode(location)
    if not geo:
        return f"I couldn't find a location called {location}. Could you be more specific?"
    
    print(f"{Fore.GREEN}[WEATHER] Found: {geo['name']}, {geo['country']} ({geo['latitude']}, {geo['longitude']}){Style.RESET_ALL}")
    
    # 2. Get current weather
    weather = get_current_weather(geo["latitude"], geo["longitude"], geo.get("timezone", "auto"))
    if not weather:
        return f"I couldn't get the weather for {geo['name']}. The weather service might be unavailable."
    
    # 3. Format response
    location_str = f"{geo['name']}, {geo['country']}" if geo['country'] else geo['name']
    temp = weather['temperature']
    feels_like = weather['feels_like']
    description = weather['weather_description']
    humidity = weather['humidity']
    wind = weather['wind_speed']
    
    # Build natural response
    response = f"In {location_str}, it's currently {temp}°C with {description}. "
    
    # Add feels like if significantly different
    if abs(temp - feels_like) >= 2:
        response += f"It feels like {feels_like}°C. "
    
    # Add humidity and wind
    response += f"Humidity is {humidity}% and wind speed is {wind} km/h."
    
    # Add precipitation warning if any
    if weather['precipitation'] > 0:
        response += f" There's {weather['precipitation']}mm of precipitation."
    
    return response


def get_weather_forecast(location: str = None, days: int = 3) -> str:
    """
    Get multi-day forecast for a location.
    Returns a natural language response.
    """
    if not location or location.strip() == "":
        location = "Chennai"
    
    print(f"{Fore.CYAN}[WEATHER] Getting {days}-day forecast for: {location}{Style.RESET_ALL}")
    
    # 1. Geocode
    geo = geocode(location)
    if not geo:
        return f"I couldn't find {location}."
    
    # 2. Get forecast
    forecast = get_forecast(geo["latitude"], geo["longitude"], days, geo.get("timezone", "auto"))
    if not forecast:
        return f"I couldn't get the forecast for {geo['name']}."
    
    # 3. Format response
    location_str = f"{geo['name']}, {geo['country']}" if geo['country'] else geo['name']
    response = f"Here's the {days}-day forecast for {location_str}: "
    
    for day in forecast[:days]:
        # Parse date
        date_obj = datetime.strptime(day['date'], "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        
        response += f"{day_name}: {day['temp_max']}/{day['temp_min']}°C, {day['weather_description']}. "
    
    return response.strip()


# Convenience functions for common queries
def is_it_raining(location: str = None) -> str:
    """Check if it's currently raining."""
    if not location:
        location = "Chennai"
    
    geo = geocode(location)
    if not geo:
        return f"I couldn't find {location}."
    
    weather = get_current_weather(geo["latitude"], geo["longitude"])
    if not weather:
        return "I couldn't check the weather right now."
    
    code = weather['weather_code']
    precipitation = weather['precipitation']
    
    # Rain codes: 51-67, 80-82, 95-99
    rain_codes = list(range(51, 68)) + list(range(80, 83)) + list(range(95, 100))
    
    if code in rain_codes or precipitation > 0:
        return f"Yes, it's currently {weather['weather_description']} in {geo['name']} with {precipitation}mm of precipitation."
    else:
        return f"No, it's not raining in {geo['name']}. The sky is {weather['weather_description']}."


def should_i_carry_umbrella(location: str = None) -> str:
    """Recommend if an umbrella is needed based on forecast."""
    if not location:
        location = "Chennai"
    
    geo = geocode(location)
    if not geo:
        return f"I couldn't find {location}."
    
    # Get today's forecast
    forecast = get_forecast(geo["latitude"], geo["longitude"], 1)
    if not forecast or len(forecast) == 0:
        return "I couldn't check the forecast."
    
    today = forecast[0]
    rain_codes = list(range(51, 68)) + list(range(80, 83)) + list(range(95, 100))
    
    if today['weather_code'] in rain_codes or today['precipitation'] > 1:
        return f"Yes, I'd recommend carrying an umbrella. {geo['name']} expects {today['weather_description']} with {today['precipitation']}mm precipitation today."
    else:
        return f"No umbrella needed for {geo['name']} today. It should be {today['weather_description']}."


# Test
if __name__ == "__main__":
    print("Testing Open-Meteo Integration...")
    print("-" * 40)
    
    # Test current weather
    print("\n1. Current weather for Chennai:")
    print(get_weather("Chennai"))
    
    print("\n2. Current weather for London:")
    print(get_weather("London"))
    
    print("\n3. 3-day forecast for Tokyo:")
    print(get_weather_forecast("Tokyo", 3))
    
    print("\n4. Is it raining in Mumbai?")
    print(is_it_raining("Mumbai"))
    
    print("\n5. Should I carry umbrella in New York?")
    print(should_i_carry_umbrella("New York"))
