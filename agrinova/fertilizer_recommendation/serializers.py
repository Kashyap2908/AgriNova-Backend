from rest_framework import serializers
from .models import FertilizerRecommendationHistory

class FertilizerRecommendationHistorySerializer(serializers.ModelSerializer):
    farm_name = serializers.SerializerMethodField()

    class Meta:
        model = FertilizerRecommendationHistory
        fields = '__all__'

    def get_farm_name(self, obj):
        return obj.farm.farm_name if obj.farm else "Custom Farm"
