from django.db import models

class WeatherCache(models.Model):
    """
    Stores weather cache for a specific farm to minimize API calls.
    Follows a strict refresh policy:
    - current: every time requested (if API fails, estimates from hourly)
    - today_hourly: every 6 hours
    - weekly_hourly & daily: every 24 hours
    """
    farm = models.OneToOneField('farms.Farm', on_delete=models.CASCADE, related_name='weather_cache')
    
    # JSON Data Stores
    current_weather = models.JSONField(null=True, blank=True)
    yesterday_hourly_forecast = models.JSONField(null=True, blank=True)
    today_hourly_forecast = models.JSONField(null=True, blank=True)
    weekly_hourly_forecast = models.JSONField(null=True, blank=True)
    daily_forecast = models.JSONField(null=True, blank=True)
    
    # Timestamps for Cache Invalidations
    current_updated_at = models.DateTimeField(null=True, blank=True)
    today_updated_at = models.DateTimeField(null=True, blank=True)
    weekly_updated_at = models.DateTimeField(null=True, blank=True)
    daily_updated_at = models.DateTimeField(null=True, blank=True)
    
    # Provider Info
    api_provider = models.CharField(max_length=50, default="open-meteo")

    def __str__(self):
        return f"Weather Cache for Farm ID: {self.farm.id}"
