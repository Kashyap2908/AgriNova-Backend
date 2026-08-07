from django.db import models
from django.contrib.auth.models import User
from farms.models import Farm

class FertilizerRecommendationHistory(models.Model):
    RECOMMENDATION_TYPE_CHOICES = [
        ('SOIL_BASED', 'Soil-Based High Accuracy Recommendation'),
        ('ESTIMATED', 'Estimated Recommendation'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Application'),
        ('APPLIED', 'Applied to Farm'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fertilizer_recommendations')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='fertilizer_recommendations', null=True, blank=True)
    crop = models.CharField(max_length=100)
    growth_stage = models.CharField(max_length=100, default='Basal / Sowing')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES, default='SOIL_BASED')
    confidence_score = models.FloatField(default=90.0, help_text="Confidence percentage (e.g. 92.5)")

    # Primary Recommendation
    recommended_fertilizer = models.CharField(max_length=150)
    dosage_per_acre_kg = models.FloatField(default=0.0, help_text="Recommended dosage per acre in kg")
    total_quantity_kg = models.FloatField(default=0.0, help_text="Total fertilizer quantity required for farm area")
    estimated_cost_inr = models.FloatField(default=0.0, help_text="Estimated cost in INR (Rupees)")
    price_per_kg_inr = models.FloatField(default=0.0)

    # Soil Health Snapshot
    nitrogen = models.FloatField(null=True, blank=True)
    phosphorus = models.FloatField(null=True, blank=True)
    potassium = models.FloatField(null=True, blank=True)
    soil_ph = models.FloatField(null=True, blank=True)
    soil_type = models.CharField(max_length=100, blank=True, null=True)

    # JSON Payloads
    nutrient_analysis = models.JSONField(default=dict, help_text="Deficit comparison matrix (N, P, K, pH)")
    nutrient_requirement = models.JSONField(default=dict, help_text="Crop nutrient requirements breakdown")
    nutrient_gap = models.JSONField(default=dict, help_text="Calculated nutrient deficit matrix")
    application_schedule = models.JSONField(default=list, help_text="Split application timeline")
    alternative_fertilizers = models.JSONField(default=list, help_text="Top candidate fertilizer plans")
    protection_plan = models.JSONField(default=dict, help_text="Weed, disease, pest, and micronutrient protection measures")
    weather_snapshot = models.JSONField(default=dict, help_text="Weather status and advisories")
    cost_summary = models.JSONField(default=dict, help_text="Itemized cost summary and grand total")
    safety_warnings = models.JSONField(default=list, help_text="Agricultural safety handling guidelines")

    ai_explanation = models.TextField(blank=True, default="", help_text="Scientifically explainable reasoning for farmer")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        farm_name = self.farm.farm_name if self.farm else "Custom Input"
        return f"{self.crop} - {self.recommended_fertilizer} ({self.recommendation_type}) for {farm_name}"
