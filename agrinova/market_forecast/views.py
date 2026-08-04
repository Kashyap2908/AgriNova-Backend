from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import MarketForecastHistory, MarketCache
from .serializers import MarketForecastHistorySerializer, MarketCacheSerializer
from .services.market_service import MarketService
from .services.market_cache_service import MarketCacheService
from .engine.market_engine import MarketEngine

from farms.models import Farm
from recommendation.models import RecommendationHistory
from ml.market_model_manager import MarketModelManager

class MarketIntelligenceView(APIView):
    """
    Refactored Market Intelligence API.
    Uses MarketCache architecture and ML Prediction model.
    1. Loads target Crop's MarketCache.
    2. Loads trained Market Prediction ML model.
    3. Predicts Next 10 Days (daily) & Next 3-4 Months (monthly trend).
    4. Returns Current Market, 7D/30D/365D Historical Charts, and Predictions in 1 response.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        farm_id = request.query_params.get('farm_id')
        requested_crop = request.query_params.get('crop')

        if not farm_id:
            return Response({"success": False, "message": "farm_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            farm = Farm.objects.get(id=farm_id, user=request.user)
        except Farm.DoesNotExist:
            return Response({"success": False, "message": "Farm not found"}, status=status.HTTP_404_NOT_FOUND)

        # 1. Determine target crop
        crop = requested_crop
        if not crop:
            latest_rec = RecommendationHistory.objects.filter(farm=farm, user=request.user).order_by('-created_at').first()
            if latest_rec:
                crop = latest_rec.recommended_crop
            else:
                crop = "Cotton" # Default fallback crop

        state = farm.state or "Gujarat"
        district = farm.district or "Rajkot"

        # 2. Load or Fetch Crop's MarketCache using MarketCacheService
        market_cache = MarketCacheService.get_or_fetch_market_cache(crop, state, district)
        current_price_info = market_cache.current_price or {}
        weekly_history = market_cache.weekly_price_history or []
        monthly_history = market_cache.monthly_price_history or []
        yearly_history = market_cache.yearly_price_history or []

        # 3. Load ML Prediction Model & Generate Predictions
        try:
            predictor = MarketModelManager.get_instance().get_predictor()
            prediction_output = predictor.predict_market_intelligence(
                current_price_info=current_price_info,
                historical_records=yearly_history or monthly_history or weekly_history
            )
        except Exception as e:
            prediction_output = {
                "short_term_10_days": [],
                "medium_term_months": [],
                "error": str(e)
            }

        # 4. Fetch market comparison data for current district
        markets_data = MarketService.get_market_data(crop, state, district)
        forecast_engine_output = MarketEngine.generate_forecast(markets_data)

        best_modal_price = current_price_info.get("modal_price", 0.0)
        best_market = current_price_info.get("market", f"{district} APMC")

        # 5. Build analytics payload with historical trends for UI graphs
        analytics_data = forecast_engine_output.get("analytics_data", {})
        analytics_data["historical_trends"] = {
            "7D": [{"date": item.get("date"), "price": item.get("modal_price")} for item in weekly_history],
            "30D": [{"date": item.get("date"), "price": item.get("modal_price")} for item in monthly_history],
            "3M": [{"date": item.get("date"), "price": item.get("modal_price")} for item in monthly_history],
            "6M": [{"date": item.get("date"), "price": item.get("modal_price")} for item in yearly_history[-180:]],
            "1Y": [{"date": item.get("date"), "price": item.get("modal_price")} for item in yearly_history]
        }

        # Save record to MarketForecastHistory for logging/history list backward compatibility
        history_rec, _ = MarketForecastHistory.objects.get_or_create(
            user=request.user,
            farm=farm,
            crop=crop,
            defaults={
                'state': state,
                'district': district,
                'best_market': best_market,
                'best_modal_price': best_modal_price,
                'markets_data': markets_data,
                'forecast_price': forecast_engine_output.get('forecast_price'),
                'price_difference': forecast_engine_output.get('price_difference'),
                'trend': forecast_engine_output.get('trend'),
                'recommendation': forecast_engine_output.get('recommendation'),
                'forecast_source': 'MarketML_Engine_V2',
                'api_source': 'data.gov.in',
                'api_timestamp': timezone.now(),
                'analytics_data': analytics_data
            }
        )

        response_payload = {
            "crop": crop,
            "state": state,
            "district": district,
            "market": best_market,
            "best_market": best_market,
            "best_modal_price": best_modal_price,
            "current_price": current_price_info,
            "weekly_price_history": weekly_history,
            "monthly_price_history": monthly_history,
            "yearly_price_history": yearly_history,
            "predictions": prediction_output,
            "markets_data": markets_data,
            "trend": forecast_engine_output.get("trend", "STABLE"),
            "analytics_data": analytics_data,
            "created_at": current_price_info.get("last_updated") or history_rec.created_at.isoformat()
        }

        return Response({
            "success": True,
            "data": response_payload,
            "cached": True
        }, status=status.HTTP_200_OK)


class CropMarketPriceView(APIView):
    """
    Dedicated endpoint for retrieving MarketCache current price for a specific crop.
    Used when farmer clicks any crop in Crop Recommendation results.
    1. Checks MarketCache. If cached today -> returns immediately.
    2. If not cached -> fetches from Market API, saves to MarketCache, and returns.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        crop = request.query_params.get('crop')
        farm_id = request.query_params.get('farm_id')

        if not crop:
            return Response({"success": False, "message": "crop parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        state = "Gujarat"
        district = "Rajkot"

        if farm_id:
            try:
                farm = Farm.objects.get(id=farm_id, user=request.user)
                state = farm.state or state
                district = farm.district or district
            except Farm.DoesNotExist:
                pass

        market_cache = MarketCacheService.get_or_fetch_market_cache(crop, state, district)
        serializer = MarketCacheSerializer(market_cache)

        return Response({
            "success": True,
            "data": {
                "crop": crop,
                "state": state,
                "district": district,
                "market": market_cache.market,
                "current_price": market_cache.current_price,
                "weekly_price_history": market_cache.weekly_price_history,
                "monthly_price_history": market_cache.monthly_price_history,
                "yearly_price_history": market_cache.yearly_price_history,
                "last_updated": market_cache.last_updated
            }
        }, status=status.HTTP_200_OK)


class MarketForecastHistoryListView(generics.ListAPIView):
    serializer_class = MarketForecastHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MarketForecastHistory.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        })


class MarketForecastHistoryDetailView(generics.RetrieveAPIView):
    serializer_class = MarketForecastHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MarketForecastHistory.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "data": serializer.data
        })


from .services.historical_service import HistoricalMarketService
from .engine.historical_engine import HistoricalEngine

class HistoricalExplorerView(APIView):
    """
    Fetches bulk historical market data and generates JSON payload for Historical Explorer.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        crop = request.query_params.get("crop")
        state = request.query_params.get("state")
        district = request.query_params.get("district", "all")
        days_str = request.query_params.get("days", "30")

        if not crop or not state:
            return Response({"success": False, "message": "crop and state are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            days = int(days_str)
        except ValueError:
            days = 30

        raw_records = HistoricalMarketService.get_historical_data(crop, state, district, days)

        if not raw_records:
            return Response({"success": False, "message": "No historical records found.", "data": None}, status=status.HTTP_404_NOT_FOUND)

        processed_data = HistoricalEngine.process_historical_data(raw_records)

        return Response({
            "success": True,
            "data": processed_data
        }, status=status.HTTP_200_OK)
