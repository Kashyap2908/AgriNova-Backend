from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from recommendation.services.recommendation_service import (
    generate_crop_recommendation,
    get_all_available_crops_for_farm
)
from recommendation.season.season_service import determine_season
from recommendation.models import RecommendationHistory
from recommendation.serializers import RecommendationHistorySerializer
from farms.models import Farm

class PredictCropView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        farm_id = request.data.get('farm_id')
        
        if not farm_id:
            return Response({
                "success": False,
                "error": "farm_id is required."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            result = generate_crop_recommendation(request.user, farm_id, request.data)
            
            return Response({
                "success": True,
                "data": result
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            print(f"[PredictCropView Error]: {traceback.format_exc()}")
            return Response({
                "success": False,
                "error": "An unexpected error occurred during crop prediction."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailableCropsView(APIView):
    """
    Returns suitable candidate crops for the selected farm's state & current season.
    Used by frontend crop comparison feature.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, farm_id):
        try:
            farm = Farm.objects.get(id=farm_id, user=request.user)
            season = determine_season()
            crops = get_all_available_crops_for_farm(farm, season)
            return Response({
                "success": True,
                "data": {
                    "crops": crops,
                    "season": season,
                    "state": farm.state
                }
            }, status=status.HTTP_200_OK)
        except Farm.DoesNotExist:
            return Response({"success": False, "error": "Farm not found."}, status=status.HTTP_404_NOT_FOUND)


class RecommendationHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = RecommendationHistory.objects.filter(user=request.user)
        serializer = RecommendationHistorySerializer(history, many=True)
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class RecommendationHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            history = RecommendationHistory.objects.get(pk=pk, user=request.user)
            serializer = RecommendationHistorySerializer(history)
            return Response({
                "success": True,
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except RecommendationHistory.DoesNotExist:
            return Response({"success": False, "error": "Recommendation history record not found."}, status=status.HTTP_404_NOT_FOUND)
