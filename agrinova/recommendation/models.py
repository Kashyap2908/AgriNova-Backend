from django.db import models
from django.contrib.auth.models import User
from farms.models import Farm

class RecommendationHistory(models.Model):
    MODE_CHOICES = [
        ('AI', 'AI Recommendation (With Soil Test Report)'),
        ('Quick', 'Quick Recommendation (No Soil Test Report)'),
    ]

    TYPE_CHOICES = [
        ('BEST', 'Recommend Best Crop'),
        ('COMPARE', 'Compare Selected Crops'),
    ]

    user = models.ForeignKey(User, related_name='recommendation_history', on_delete=models.CASCADE)
    farm = models.ForeignKey(Farm, related_name='recommendation_history', on_delete=models.CASCADE)
    
    recommendation_mode = models.CharField(max_length=50, choices=MODE_CHOICES, default='AI')
    recommendation_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='BEST')

    input_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="Stores input soil values (N, P, K, pH, water_requirement) and requested comparison crops"
    )

    weather_snapshot = models.JSONField(
        default=dict,
        help_text="Stores 7-day temp avg, 7-day humidity avg, 7-day cumulative rainfall, description"
    )

    recommended_crop = models.CharField(max_length=255)
    expected_yield = models.FloatField(null=True, blank=True, help_text="Expected yield in kg/ha")
    confidence = models.FloatField(default=0.0, help_text="Confidence percentage")

    results_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete structured prediction and comparison output"
    )

    explanation = models.JSONField(
        default=list,
        blank=True,
        help_text="List of key reasons explaining why the crop was recommended"
    )
    
    prediction_source = models.CharField(max_length=100, default='ML Model')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recommended_crop} ({self.recommendation_mode}/{self.recommendation_type}) for {self.farm.farm_name} ({self.created_at.date()})"
