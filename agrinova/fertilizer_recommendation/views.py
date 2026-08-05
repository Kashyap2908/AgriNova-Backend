from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .models import FertilizerRecommendationHistory
from .serializers import FertilizerRecommendationHistorySerializer
from .services.fertilizer_service import FertilizerService
from ml.fertilizer_predictor import FertilizerPredictor
from farms.models import Farm

class FertilizerRecommendView(APIView):
    """
    POST /api/fertilizer/recommend/
    Primary endpoint for generating smart fertilizer recommendations.
    Accepts:
    - farm_id (required)
    - growth_stage (optional)
    - soil_overrides (optional N, P, K, pH)
    Automatically branches to Soil-Based or Estimated decision paths.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        farm_id = request.data.get('farm_id')
        growth_stage = request.data.get('growth_stage')
        soil_overrides = request.data.get('soil_overrides')

        if not farm_id:
            return Response({"success": False, "message": "farm_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = FertilizerService.generate_recommendation(
                farm_id=int(farm_id),
                user=request.user,
                growth_stage=growth_stage,
                soil_overrides=soil_overrides
            )
            return Response({"success": True, "data": result}, status=status.HTTP_200_OK)
        except Farm.DoesNotExist:
            return Response({"success": False, "message": "Farm not found or access denied."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "message": f"Recommendation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FertilizerHistoryListView(generics.ListAPIView):
    """
    GET /api/fertilizer/history/
    Lists past recommendation records for the user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FertilizerRecommendationHistorySerializer

    def get_queryset(self):
        farm_id = self.request.query_params.get('farm_id')
        qs = FertilizerRecommendationHistory.objects.filter(user=self.request.user)
        if farm_id:
            qs = qs.filter(farm_id=farm_id)
        return qs.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


class FertilizerMasterListView(APIView):
    """
    GET /api/fertilizer/master/
    Returns reference catalog of official Indian fertilizers.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        predictor = FertilizerPredictor()
        return Response({"success": True, "data": predictor.fertilizer_master}, status=status.HTTP_200_OK)
