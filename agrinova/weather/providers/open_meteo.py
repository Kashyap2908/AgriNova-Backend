import requests
from datetime import datetime
import json

def fetch_weather_from_api(lat, lon, fetch_current=False, fetch_hourly=False, fetch_daily=False):
    """
    Fetches raw weather data from Open-Meteo based on selective flags.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "past_days": 1,
    }
    
    if fetch_current:
        params["current"] = "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
    if fetch_hourly:
        params["hourly"] = "temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m"
    if fetch_daily:
        params["daily"] = "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,precipitation_probability_max,uv_index_max"

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
