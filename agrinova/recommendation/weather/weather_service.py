import requests
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Weather code descriptions mapping based on WMO Weather interpretation codes
WEATHER_CODES = {
    0: 'Clear sky',
    1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
    45: 'Fog', 48: 'Depositing rime fog',
    51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle',
    61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
    71: 'Slight snow fall', 73: 'Moderate snow fall', 75: 'Heavy snow fall',
    95: 'Thunderstorm', 96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail',
}

def get_weather_description(code):
    return WEATHER_CODES.get(code, 'Unknown weather')

def fetch_current_weather(latitude: float, longitude: float) -> dict:
    """
    Fetches weather data from Open-Meteo API.
    Caches the response for 30 minutes to reduce API requests.
    """
    if not latitude or not longitude:
        return {}

    cache_key = f"weather_{round(latitude, 2)}_{round(longitude, 2)}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation", 
                    "surface_pressure", "wind_speed_10m", "cloud_cover", "weather_code"]
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        
        weather_data = {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "rainfall": current.get("precipitation"),
            "wind_speed": current.get("wind_speed_10m"),
            "pressure": current.get("surface_pressure"),
            "cloud_cover": current.get("cloud_cover"),
            "description": get_weather_description(current.get("weather_code", -1))
        }
        
        # Cache for 30 minutes (1800 seconds)
        cache.set(cache_key, weather_data, timeout=1800)
        return weather_data
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return {
            "temperature": None,
            "humidity": None,
            "rainfall": None,
            "wind_speed": None,
            "pressure": None,
            "cloud_cover": None,
            "description": "Weather data unavailable"
        }
