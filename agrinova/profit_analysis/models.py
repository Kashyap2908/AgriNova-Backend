from django.db import models
from django.contrib.auth.models import User
from farms.models import Farm
from recommendation.models import RecommendationHistory

class ProfitAnalysisHistory(models.Model):
    user = models.ForeignKey(User, related_name='profit_analyses', on_delete=models.CASCADE)
    farm = models.ForeignKey(Farm, related_name='profit_analyses', on_delete=models.CASCADE)
    recommendation_history = models.ForeignKey(
        RecommendationHistory, 
        related_name='profit_analyses', 
        on_delete=models.CASCADE, 
        null=True, blank=True
    )
    
    crop = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    farm_area = models.FloatField()
    area_unit = models.CharField(max_length=20, default='Acre')
    
    expected_yield_total = models.FloatField(help_text="Total yield in Quintals")
    predicted_market_price = models.FloatField(help_text="Predicted 3-month harvest price in INR/Quintal")
    
    cost_breakdown = models.JSONField(default=dict, help_text="Individual costs and source info")
    financial_summary = models.JSONField(default=dict, help_text="Gross Income, Net Profit, ROI, Profit Margin, Break-even Price")
    scenarios = models.JSONField(default=dict, help_text="Best, Average, Worst case metrics")
    risk_analysis = models.JSONField(default=dict, help_text="Risk level and risk factors")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Profit Analysis for {self.crop} ({self.farm.farm_name}) - {self.created_at.date()}"
