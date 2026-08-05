from weather.models import WeatherCache

def get_weather_context(farm_id):
    try:
        cache = WeatherCache.objects.get(farm_id=farm_id)
        return {
            "available": True,
            "current_weather": cache.current_weather or "Data unavailable",
            "daily_forecast": cache.daily_forecast or "Data unavailable"
        }
    except WeatherCache.DoesNotExist:
        return {
            "available": False,
            "message": "Weather data is currently unavailable for this farm. Do not make assumptions about the weather."
        }
