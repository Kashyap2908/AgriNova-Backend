from rest_framework import serializers
from recommendation.models import RecommendationHistory

class RecommendationHistorySerializer(serializers.ModelResourceSerializer if hasattr(serializers, 'ModelResourceSerializer') else serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.farm_name', read_only=True)
    farm_state = serializers.CharField(source='farm.state', read_only=True)
    farm_location = serializers.SerializerMethodField()
    season = serializers.SerializerMethodField()

    class Meta:
        model = RecommendationHistory
        fields = [
            'id',
            'farm',
            'farm_name',
            'farm_state',
            'farm_location',
            'recommendation_mode',
            'recommendation_type',
            'recommended_crop',
            'expected_yield',
            'confidence',
            'season',
            'weather_snapshot',
            'input_values',
            'results_payload',
            'explanation',
            'prediction_source',
            'created_at',
            'updated_at'
        ]

    def get_farm_location(self, obj):
        if obj.farm:
            return f"{obj.farm.village}, {obj.farm.district}, {obj.farm.state}"
        return ""

    def get_season(self, obj):
        if obj.results_payload and isinstance(obj.results_payload, dict):
            return obj.results_payload.get('season', 'Kharif')
        from recommendation.season.season_service import determine_season
        return determine_season()

