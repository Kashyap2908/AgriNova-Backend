from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from recommendation.services.recommendation_service import generate_crop_recommendation
from recommendation.models import RecommendationHistory
from recommendation.serializers import RecommendationHistorySerializer

class PredictCropView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        farm_id = request.data.get('farm_id')
        
        if not farm_id:
            return Response({"error": "farm_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Delegate all business logic to the service layer
            result = generate_crop_recommendation(request.user, farm_id)
            
            return Response({
                "success": True,
                "data": result
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "An unexpected error occurred during prediction."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecommendationHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = RecommendationHistory.objects.filter(user=request.user)
        serializer = RecommendationHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecommendationHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            history = RecommendationHistory.objects.get(pk=pk, user=request.user)
            serializer = RecommendationHistorySerializer(history)
            
            # For the detail view, we might want to return the full feature snapshot too
            # We'll just attach it to the standard serialized data for debugging
            data = serializer.data
            data['feature_snapshot'] = history.feature_snapshot
            
            return Response(data, status=status.HTTP_200_OK)
        except RecommendationHistory.DoesNotExist:
            return Response({"error": "Recommendation history not found."}, status=status.HTTP_404_NOT_FOUND)
