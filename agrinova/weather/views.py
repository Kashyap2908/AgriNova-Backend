from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from farms.models import Farm
from .services import WeatherCacheService

class WeatherDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        farm_id = request.query_params.get('farm_id')
        
        if not farm_id:
            return Response({"success": False, "error": "farm_id is required."}, status=400)

        # Validate farm ownership to prevent users from querying other people's farms
        farm = get_object_or_404(Farm, id=farm_id, user=request.user)

        # The service handles caching, refreshing, and DB locking internally
        weather_data = WeatherCacheService.get_weather_data(farm.id)

        return Response({
            "success": True,
            "data": weather_data
        })
