import requests
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

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
    return WEATHER_CODES.get(code, 'Partly cloudy')

def fetch_current_weather(latitude: float, longitude: float) -> dict:
    """
    Fetches 7-day weather data from Open-Meteo API.
    Calculates:
    - 7-day average Temperature (°C)
    - 7-day average Humidity (%)
    - 7-day cumulative Rainfall (mm)
    Caches the response for 60 minutes to optimize performance.
    """
    if latitude is None or longitude is None:
        return {
            "temperature": 26.5,
            "humidity": 65.0,
            "rainfall": 120.0,
            "description": "Default regional climate",
            "is_fallback": True
        }

    cache_key = f"weather_7day_{round(float(latitude), 2)}_{round(float(longitude), 2)}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "past_days": 3,
        "forecast_days": 4,
        "daily": ["temperature_2m_max", "temperature_2m_min", "relative_humidity_2m_mean", "precipitation_sum", "weather_code"]
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get("daily", {})
        
        temps_max = daily.get("temperature_2m_max", [])
        temps_min = daily.get("temperature_2m_min", [])
        humidities = daily.get("relative_humidity_2m_mean", [])
        precip = daily.get("precipitation_sum", [])
        codes = daily.get("weather_code", [])

        # Compute 7-day average temperature
        daily_temps = []
        for t_max, t_min in zip(temps_max, temps_min):
            if t_max is not None and t_min is not None:
                daily_temps.append((t_max + t_min) / 2.0)

        avg_temp = sum(daily_temps) / len(daily_temps) if daily_temps else 26.5

        # Compute 7-day average humidity
        valid_humi = [h for h in humidities if h is not None]
        avg_humidity = sum(valid_humi) / len(valid_humi) if valid_humi else 65.0

        # Compute 7-day cumulative rainfall
        valid_precip = [p for p in precip if p is not None]
        cum_rainfall = sum(valid_precip) if valid_precip else 0.0

        latest_code = codes[-1] if codes else 0

        weather_data = {
            "temperature": round(float(avg_temp), 1),
            "humidity": round(float(avg_humidity), 1),
            "rainfall": round(float(cum_rainfall), 1),
            "description": get_weather_description(latest_code),
            "is_7day_summary": True,
            "period": "7-day window (3 past + 4 forecast)"
        }
        
        # Cache for 60 minutes (3600 seconds)
        cache.set(cache_key, weather_data, timeout=3600)
        return weather_data
        
    except Exception as e:
        logger.error(f"Failed to fetch 7-day weather data from Open-Meteo: {e}")
        return {
            "temperature": 26.5,
            "humidity": 65.0,
            "rainfall": 120.0,
            "description": "Estimated regional climate",
            "is_fallback": True
        }
