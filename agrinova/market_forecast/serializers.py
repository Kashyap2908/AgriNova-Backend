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
    crop = serializers.CharField(required=False, allow_blank=True)


from .models import MarketCache

class MarketCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketCache
        fields = [
            'id', 'crop', 'state', 'district', 'market',
            'current_price', 'weekly_price_history', 'monthly_price_history',
            'yearly_price_history', 'last_updated', 'api_provider'
        ]

