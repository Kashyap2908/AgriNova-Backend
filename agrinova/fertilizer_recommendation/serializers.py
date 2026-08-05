from rest_framework import serializers
from .models import FertilizerRecommendationHistory

class FertilizerRecommendationHistorySerializer(serializers.ModelSerializer):
    farm_name = serializers.ReadOnlyField(source='farm.farm_name')

    class Meta:
        model = FertilizerRecommendationHistory
        fields = '__all__'
