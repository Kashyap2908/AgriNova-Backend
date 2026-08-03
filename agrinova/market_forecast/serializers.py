from rest_framework import serializers
from .models import MarketForecastHistory
from farms.models import Farm

class MarketForecastHistorySerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.farm_name', read_only=True)
    village = serializers.CharField(source='farm.village', read_only=True)

    class Meta:
        model = MarketForecastHistory
        fields = [
            'id', 'farm', 'farm_name', 'village', 'crop', 'state', 'district',
            'best_market', 'best_modal_price', 'markets_data',
            'forecast_price', 'price_difference', 'trend', 
            'recommendation', 'forecast_source',
            'api_source', 'resource_id', 'api_timestamp',
            'analytics_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class MarketPredictRequestSerializer(serializers.Serializer):
    farm_id = serializers.IntegerField(required=True)
