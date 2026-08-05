from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from farms.models import Farm
from .models import WeatherCache
from .providers.open_meteo import fetch_weather_from_api
import logging

logger = logging.getLogger(__name__)

class WeatherCacheService:

    @staticmethod
    def get_weather_data(farm_id: int) -> dict:
        """
        Main entry point. Returns the unified JSON object for the frontend.
        Automatically handles lazy midnight rotation, cache invalidations, and fallback logic.
        """
        cache, created = WeatherCache.objects.get_or_create(farm_id=farm_id)
        farm = cache.farm

        now = timezone.now()

        # 1. Lazy Midnight Rotation
        WeatherCacheService._check_and_perform_midnight_rotation(cache, now)

        # 2. Determine what needs fetching
        needs_today = False
        needs_weekly_daily = False

        if not cache.today_updated_at or (now - cache.today_updated_at) > timedelta(hours=6):
            needs_today = True

        if not cache.daily_updated_at or (now - cache.daily_updated_at) > timedelta(hours=24):
            needs_weekly_daily = True

        # 3. Always attempt to fetch current weather
        fetch_current = True
        
        # Fetch from API outside long DB transaction
        try:
            fetch_hourly = needs_today or needs_weekly_daily
            
            api_data = fetch_weather_from_api(
                lat=farm.latitude or 23.2599, 
                lon=farm.longitude or 77.4126,
                fetch_current=fetch_current,
                fetch_hourly=fetch_hourly,
                fetch_daily=needs_weekly_daily
            )
            
            # Update Current
            if "current" in api_data:
                cache.current_weather = WeatherCacheService._parse_current(api_data["current"])
                cache.current_updated_at = now
            
            # Update Hourly (Today & Weekly)
            if "hourly" in api_data:
                hourly = api_data["hourly"]
                if needs_today:
                    cache.today_hourly_forecast = WeatherCacheService._parse_today_hourly(hourly, now)
                    cache.today_updated_at = now
                if needs_weekly_daily:
                    cache.weekly_hourly_forecast = WeatherCacheService._parse_weekly_hourly(hourly, now)
            
            # Update Daily
            if "daily" in api_data and needs_weekly_daily:
                cache.daily_forecast = WeatherCacheService._parse_daily(api_data["daily"])
                cache.daily_updated_at = now
                cache.weekly_updated_at = now # Sync weekly marker

        except Exception as e:
            logger.error(f"Weather API Error: {e}")
            # Fallback Logic for Current Weather
            if not cache.current_weather or (now - cache.current_updated_at) > timedelta(hours=1):
                cache.current_weather = WeatherCacheService._estimate_current_from_hourly(cache.today_hourly_forecast, now)

        cache.save()
        
        return {
            "current_weather": cache.current_weather,
            "yesterday_hourly_forecast": cache.yesterday_hourly_forecast,
            "today_hourly_forecast": cache.today_hourly_forecast,
            "weekly_hourly_forecast": cache.weekly_hourly_forecast,
            "daily_forecast": cache.daily_forecast,
        }

    @staticmethod
    def _check_and_perform_midnight_rotation(cache: WeatherCache, now):
        """
        Lazy rotation. If current time is on a new day compared to today_updated_at, rotate.
        """
        if not cache.today_updated_at:
            return # Nothing to rotate yet
            
        # Check if dates are different (ignoring time)
        local_now_date = now.date()
        local_cache_date = cache.today_updated_at.date()
        
        days_diff = (local_now_date - local_cache_date).days
        
        if days_diff >= 1:
            # It's a new day! Perform rotation.
            
            if days_diff == 1:
                # Move today to yesterday
                cache.yesterday_hourly_forecast = cache.today_hourly_forecast
            else:
                # More than 1 day passed, yesterday is invalid
                cache.yesterday_hourly_forecast = None
                
            # Clear today so it gets refetched
            cache.today_hourly_forecast = None
            cache.today_updated_at = None
            
            # The prompt says: "Shift weekly_hourly_forecast forward by one day."
            # Since we refresh weekly every 24h anyway, clearing it forces a fresh refetch.
            cache.weekly_hourly_forecast = None
            cache.weekly_updated_at = None
            cache.daily_forecast = None
            cache.daily_updated_at = None

    @staticmethod
    def _parse_current(current_data: dict) -> dict:
        return {
            "temperature": current_data.get("temperature_2m"),
            "feels_like": current_data.get("apparent_temperature"),
            "humidity": current_data.get("relative_humidity_2m"),
            "wind_speed": current_data.get("wind_speed_10m"),
            "rainfall": current_data.get("precipitation"),
            "weather_code": current_data.get("weather_code"),
            "timestamp": current_data.get("time")
        }

    @staticmethod
    def _parse_today_hourly(hourly_data: dict, now) -> list:
        today_str = now.strftime('%Y-%m-%d')
        result = []
        for i, time_str in enumerate(hourly_data.get("time", [])):
            if time_str.startswith(today_str):
                result.append({
                    "time": time_str,
                    "temperature": hourly_data["temperature_2m"][i],
                    "humidity": hourly_data["relative_humidity_2m"][i],
                    "precipitation_probability": hourly_data["precipitation_probability"][i],
                    "weather_code": hourly_data["weather_code"][i],
                    "wind_speed": hourly_data["wind_speed_10m"][i],
                })
        return result

    @staticmethod
    def _parse_weekly_hourly(hourly_data: dict, now) -> list:
        today_str = now.strftime('%Y-%m-%d')
        yesterday_str = (now - timedelta(days=1)).strftime('%Y-%m-%d')
        result = []
        for i, time_str in enumerate(hourly_data.get("time", [])):
            if not time_str.startswith(today_str) and not time_str.startswith(yesterday_str):
                result.append({
                    "time": time_str,
                    "temperature": hourly_data["temperature_2m"][i],
                    "weather_code": hourly_data["weather_code"][i],
                })
        return result

    @staticmethod
    def _parse_daily(daily_data: dict) -> list:
        result = []
        for i, time_str in enumerate(daily_data.get("time", [])):
            result.append({
                "date": time_str,
                "max_temp": daily_data["temperature_2m_max"][i],
                "min_temp": daily_data["temperature_2m_min"][i],
                "sunrise": daily_data["sunrise"][i],
                "sunset": daily_data["sunset"][i],
                "rainfall": daily_data["precipitation_sum"][i],
                "rain_probability": daily_data["precipitation_probability_max"][i],
                "weather_code": daily_data["weather_code"][i],
                "uv_index_max": daily_data.get("uv_index_max", [0]*len(daily_data["time"]))[i] if "uv_index_max" in daily_data else 0,
            })
        return result

    @staticmethod
    def _estimate_current_from_hourly(today_hourly: list, now) -> dict:
        if not today_hourly:
            return {"error": "Cannot estimate weather, no hourly data available."}
            
        current_hour_str = now.strftime('%Y-%m-%dT%H:00')
        for hour_data in today_hourly:
            if hour_data["time"] == current_hour_str:
                return {
                    "temperature": hour_data["temperature"],
                    "feels_like": hour_data["temperature"],
                    "humidity": hour_data["humidity"],
                    "wind_speed": hour_data["wind_speed"],
                    "rainfall": 0,
                    "weather_code": hour_data["weather_code"],
                    "timestamp": now.isoformat(),
                    "is_estimated": True
                }
        
        return {
            "temperature": today_hourly[0]["temperature"],
            "weather_code": today_hourly[0]["weather_code"],
            "is_estimated": True
        }
