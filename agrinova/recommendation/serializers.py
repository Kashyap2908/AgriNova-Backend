from rest_framework import serializers
from recommendation.models import RecommendationHistory

class RecommendationHistorySerializer(serializers.ModelSerializer):
    farm_name = serializers.ReadOnlyField(source='farm.farm_name')
    
    class Meta:
        model = RecommendationHistory
        fields = [
            'id',
            'farm_name',
            'recommended_crop',
            'confidence',
            'season',
            'weather_snapshot',
            'prediction_source',
            'created_at'
        ]
