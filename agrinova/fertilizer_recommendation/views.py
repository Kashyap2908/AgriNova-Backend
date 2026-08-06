"""
Fertilizer Recommendation API Views
Exposes REST endpoints for generating smart dynamic fertilizer recommendations and history retrieval.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .models import FertilizerRecommendationHistory
from .serializers import FertilizerRecommendationHistorySerializer
from .services.recommendation_engine import SmartFertilizerEngine
from farms.models import Farm


class FertilizerRecommendView(APIView):
    """
    POST /api/fertilizer/recommend/
    Primary endpoint for generating smart fertilizer recommendations.
    Accepts farm_id OR custom payload (crop, nitrogen, phosphorus, potassium, ph, soil_type, state, season, farm_area, previous_crop).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data or {}
        farm_id = data.get('farm_id')
        
        crop = data.get('crop')
        nitrogen = data.get('nitrogen')
        phosphorus = data.get('phosphorus')
        potassium = data.get('potassium')
        ph = data.get('ph')
        soil_type = data.get('soil_type')
        state_param = data.get('state')
        season = data.get('season')
        farm_area = data.get('farm_area')
        previous_crop = data.get('previous_crop', '')
        force_mode = data.get('force_mode') or data.get('mode')

        farm_obj = None
        if farm_id:
            try:
                farm_obj = Farm.objects.get(id=farm_id, user=request.user)
                # Auto-populate fields from farm profile safely if omitted
                crop = crop or getattr(farm_obj, 'current_crop', None) or getattr(farm_obj, 'crop', None) or 'Wheat'
                soil_type = soil_type or getattr(farm_obj, 'soil_type', None) or 'Loamy'
                state_param = state_param or getattr(farm_obj, 'state', None) or 'Punjab'
                season_param = season or getattr(farm_obj, 'season', None) or 'Kharif'
                farm_area = farm_area or getattr(farm_obj, 'farm_area', None) or getattr(farm_obj, 'area_acres', None) or 1.0

                # Extract soil NPK from farm profile if available and not overridden
                if nitrogen is None:
                    nitrogen = getattr(farm_obj, 'nitrogen', None)
                if phosphorus is None:
                    phosphorus = getattr(farm_obj, 'phosphorus', None)
                if potassium is None:
                    potassium = getattr(farm_obj, 'potassium', None)
                if ph is None:
                    ph = getattr(farm_obj, 'soil_ph', None) or getattr(farm_obj, 'ph_level', None)

            except Farm.DoesNotExist:
                return Response({"success": False, "message": "Farm not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        # Instantiate engine
        engine = SmartFertilizerEngine()

        try:
            res = engine.generate_recommendation(
                farm_id=int(farm_id) if farm_id else None,
                crop=crop or 'Wheat',
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                ph=ph,
                soil_type=soil_type or 'Loamy',
                state=state_param or 'Punjab',
                season=season or 'Kharif',
                farm_area=float(farm_area or 1.0),
                previous_crop=previous_crop or '',
                force_mode=force_mode
            )

            # Record history if farm exists
            if farm_obj and res.get('primary_recommendation'):
                primary = res['primary_recommendation']
                items = primary.get('items', [])
                first_item = items[0] if items else {}
                
                rec_history = FertilizerRecommendationHistory.objects.create(
                    user=request.user,
                    farm=farm_obj,
                    crop=crop or 'Wheat',
                    growth_stage='Basal / Split Schedule',
                    recommendation_type='SOIL_BASED' if res.get('mode') == 'PRECISION' else 'ESTIMATED',
                    confidence_score=primary.get('score', 90.0),
                    recommended_fertilizer=primary.get('title', 'Fertilizer Combo'),
                    dosage_per_acre_kg=first_item.get('dose_per_acre_kg', 0.0),
                    total_quantity_kg=first_item.get('total_quantity_kg', 0.0),
                    estimated_cost_inr=primary.get('total_cost_inr', 0.0),
                    price_per_kg_inr=first_item.get('price_per_kg', 0.0),
                    nitrogen=float(nitrogen) if nitrogen is not None else None,
                    phosphorus=float(phosphorus) if phosphorus is not None else None,
                    potassium=float(potassium) if potassium is not None else None,
                    soil_ph=float(ph) if ph is not None else None,
                    soil_type=soil_type or 'Loamy',
                    nutrient_analysis={},
                    application_schedule=res.get('application_schedule', []),
                    alternative_fertilizers=res.get('alternative_options', []),
                    weather_snapshot={'advice': res.get('ai_explanation', {}).get('weather_advice', [])},
                    safety_warnings=res.get('agronomic_advice', {}).get('precautions', []),
                    ai_explanation=res['ai_explanation'].get('overview', '')
                )
                res['recommendation_id'] = rec_history.id

            return Response({"success": True, "data": res}, status=status.HTTP_200_OK)

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
        from .services.fertilizer_catalog import FertilizerCatalog
        catalog = FertilizerCatalog.get_all_fertilizers()
        return Response({"success": True, "data": catalog}, status=status.HTTP_200_OK)
