from django.db import models
from django.contrib.auth.models import User
from farms.models import Farm

class RecommendationHistory(models.Model):
    user = models.ForeignKey(User, related_name='recommendation_history', on_delete=models.CASCADE)
    farm = models.ForeignKey(Farm, related_name='recommendation_history', on_delete=models.CASCADE)
    
    recommended_crop = models.CharField(max_length=255)
    confidence = models.FloatField()
    season = models.CharField(max_length=50)
    
    weather_snapshot = models.JSONField(
        help_text="Stores temperature, humidity, rainfall, wind_speed, pressure, description, cloud_cover"
    )
    feature_snapshot = models.JSONField(
        help_text="Stores ML input: nitrogen, phosphorus, potassium, soil_ph, temperature, humidity, rainfall, season"
    )
    
    prediction_source = models.CharField(max_length=100, default='Dummy')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recommended_crop} for {self.farm.farm_name} ({self.created_at.date()})"
