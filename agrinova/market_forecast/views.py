from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import MarketForecastHistory
from .serializers import MarketForecastHistorySerializer
from .services.market_service import MarketService
from .engine.market_engine import MarketEngine

from farms.models import Farm
from recommendation.models import RecommendationHistory

class MarketIntelligenceView(APIView):
    """
    Zero-click Market Intelligence API.
    Fetches the latest intelligence for a given farm_id via GET.
    If a recent record (last 45 mins) exists, returns it from DB to save API calls.
    Otherwise, fetches live data, processes via MarketEngine, saves history, and returns.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        farm_id = request.query_params.get('farm_id')
        
        if not farm_id:
            return Response({"success": False, "message": "farm_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            farm = Farm.objects.get(id=farm_id, user=request.user)
        except Farm.DoesNotExist:
            return Response({"success": False, "message": "Farm not found"}, status=status.HTTP_404_NOT_FOUND)

        # 1. Check for recent intelligence in the DB (Cache for 45 mins)
        recent_threshold = timezone.now() - timedelta(minutes=45)
        recent_history = MarketForecastHistory.objects.filter(
            farm=farm, 
            user=request.user,
            created_at__gte=recent_threshold
        ).order_by('-created_at').first()
        
        if recent_history:
            return Response({
                "success": True,
                "data": MarketForecastHistorySerializer(recent_history).data,
                "cached": True
            }, status=status.HTTP_200_OK)

        # 2. If no recent history, automatically fetch the latest recommended crop
        latest_recommendation = RecommendationHistory.objects.filter(farm=farm, user=request.user).order_by('-created_at').first()
        
        if not latest_recommendation:
            return Response({
                "success": False, 
                "message": "No crop recommendation found for this farm. Please run Crop Recommendation first."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        crop = latest_recommendation.recommended_crop
        state = farm.state
        district = farm.district

        # 3. Fetch live normalized market data via Service
        api_timestamp = timezone.now()
        markets_data = MarketService.get_market_data(crop, state, district)
        
        if not markets_data:
            return Response({
                "success": False, 
                "message": f"No market data found for {crop} in {district}, {state}."
            }, status=status.HTTP_404_NOT_FOUND)

        # 4. Identify best market
        best_market_obj = markets_data[0]
        best_market = best_market_obj.get("market", "Unknown")
        best_modal_price = best_market_obj.get("modal_price", 0.0)

        # 5. Generate intelligence via Engine
        forecast = MarketEngine.generate_forecast(markets_data)

        # 6. Save new History record
        history = MarketForecastHistory.objects.create(
            user=request.user,
            farm=farm,
            recommendation_history=latest_recommendation,
            crop=crop,
            state=state,
            district=district,
            best_market=best_market,
            best_modal_price=best_modal_price,
            markets_data=markets_data,
            forecast_price=forecast.get('forecast_price'),
            price_difference=forecast.get('price_difference'),
            trend=forecast.get('trend'),
            recommendation=forecast.get('recommendation'),
            forecast_source="MarketEngine_V1",
            api_source="data.gov.in",
            resource_id="9ef84268-d588-465a-a308-a864a43d0070",
            api_timestamp=api_timestamp,
            analytics_data=forecast.get('analytics_data', {})
        )

        response_data = MarketForecastHistorySerializer(history).data
        response_data['confidence'] = forecast.get('confidence')

        return Response({
            "success": True,
            "data": response_data,
            "cached": False
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

