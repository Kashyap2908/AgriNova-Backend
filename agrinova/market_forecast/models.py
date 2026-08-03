from django.db import models
from django.contrib.auth.models import User
from farms.models import Farm
from recommendation.models import RecommendationHistory

class MarketForecastHistory(models.Model):
    user = models.ForeignKey(User, related_name='market_forecasts', on_delete=models.CASCADE)
    farm = models.ForeignKey(Farm, related_name='market_forecasts', on_delete=models.CASCADE)
    recommendation_history = models.ForeignKey(
        RecommendationHistory, 
        related_name='market_forecasts', 
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    
    crop = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    
    # Best Market Fields for easy access
    best_market = models.CharField(max_length=255)
    best_modal_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Store complete list of normalized market data
    markets_data = models.JSONField(default=list)
    
    # Forecast Engine Outputs
    forecast_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_difference = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    trend = models.CharField(max_length=50, null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    forecast_source = models.CharField(max_length=100, default='MarketEngine_V1')
    
    # API Metadata
    api_source = models.CharField(max_length=100, default="data.gov.in")
    resource_id = models.CharField(max_length=255, default="9ef84268-d588-465a-a308-a864a43d0070")
    api_timestamp = models.DateTimeField(null=True, blank=True)
    
    # Advanced Analytics Data
    analytics_data = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.crop} - {self.best_market} for {self.user.username}"
