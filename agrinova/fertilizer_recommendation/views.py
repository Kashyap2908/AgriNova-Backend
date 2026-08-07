import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from farms.models import Farm
from .models import FertilizerRecommendationHistory
from .serializers import FertilizerRecommendationHistorySerializer
from .services.planner import CropNutritionPlanner
from .services.data_loader import load_fertilizer_master, load_crop_list

logger = logging.getLogger(__name__)


class CropNutritionPlanView(APIView):
    """
    POST /api/fertilizer/plan/
    Generates a complete Smart Crop Nutrition & Protection Plan.
    Accepts either farm_id (loads farm details) OR custom parameters.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            data = request.data or {}
            farm_id = data.get('farm_id')

            farm = None
            if farm_id:
                try:
                    farm = Farm.objects.get(id=farm_id, user=request.user)
                except Farm.DoesNotExist:
                    return Response(
                        {"success": False, "message": f"Farm with ID {farm_id} not found or access denied."},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Helper function to get value from request data or farm model
            def _get_val(key, farm_attr=None):
                if data.get(key) is not None and str(data.get(key)).strip() != '':
                    return data.get(key)
                if farm and farm_attr:
                    return getattr(farm, farm_attr, None)
                return None

            if farm:
                crop = data.get('crop') or getattr(farm, 'current_crop', 'Wheat') or 'Wheat'
                farm_area = float(data.get('farm_area') or farm.farm_area or 1.0)
                area_unit = data.get('area_unit') or getattr(farm, 'area_unit', 'Acres') or 'Acres'
                soil_type = data.get('soil_type') or farm.soil_type or 'Loamy'
                state = data.get('state') or farm.state or 'Punjab'
                season = data.get('season') or 'Kharif'
                previous_crop = data.get('previous_crop', '')
            else:
                crop = data.get('crop', 'Wheat')
                farm_area = float(data.get('farm_area', 1.0) or 1.0)
                area_unit = data.get('area_unit', 'Acres')
                soil_type = data.get('soil_type', 'Loamy')
                state = data.get('state', 'Punjab')
                season = data.get('season', 'Kharif')
                previous_crop = data.get('previous_crop', '')

            nitrogen = _get_val('nitrogen', 'nitrogen')
            phosphorus = _get_val('phosphorus', 'phosphorus')
            potassium = _get_val('potassium', 'potassium')
            soil_ph = _get_val('soil_ph', 'soil_ph') or _get_val('soilPh', 'soil_ph')
            sulphur = _get_val('sulphur', 'sulphur')
            calcium = _get_val('calcium', 'calcium')
            magnesium = _get_val('magnesium', 'magnesium')
            zinc = _get_val('zinc', 'zinc')
            boron = _get_val('boron', 'boron')
            iron = _get_val('iron', 'iron')
            manganese = _get_val('manganese', 'manganese')
            copper = _get_val('copper', 'copper')
            organic_carbon = _get_val('organic_carbon', 'organic_carbon') or _get_val('organicCarbon', 'organic_carbon')
            electrical_conductivity = _get_val('electrical_conductivity', 'electrical_conductivity') or _get_val('electricalConductivity', 'electrical_conductivity')
            soil_moisture = _get_val('soil_moisture', 'soil_moisture') or _get_val('soilMoisture', 'soil_moisture')

            # Generate full plan via CropNutritionPlanner
            plan = CropNutritionPlanner.generate_plan(
                crop=crop,
                farm_area=farm_area,
                area_unit=area_unit,
                soil_type=soil_type,
                state=state,
                season=season,
                previous_crop=previous_crop,
                farm_id=farm.id if farm else None,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                soil_ph=soil_ph,
                sulphur=sulphur,
                calcium=calcium,
                magnesium=magnesium,
                zinc=zinc,
                boron=boron,
                iron=iron,
                manganese=manganese,
                copper=copper,
                organic_carbon=organic_carbon,
                electrical_conductivity=electrical_conductivity,
                soil_moisture=soil_moisture
            )

            # Persist to history database
            primary_plan = plan['top_fertilizer_plans'][0] if plan['top_fertilizer_plans'] else {}
            first_item = primary_plan.get('items', [{}])[0] if primary_plan.get('items') else {}
            item_total_kg = first_item.get('total_quantity_kg') or first_item.get('total_kg', 0.0)

            rec_history = FertilizerRecommendationHistory.objects.create(
                user=request.user,
                farm=farm,
                crop=crop,
                growth_stage='Basal / Sowing',
                recommendation_type=plan['soil_summary']['mode'],
                confidence_score=primary_plan.get('score', 92.5),
                recommended_fertilizer=first_item.get('name', 'NPK Complex'),
                dosage_per_acre_kg=first_item.get('dose_per_ha', 0.0) * 0.4047,
                total_quantity_kg=item_total_kg,
                estimated_cost_inr=plan['cost_summary']['grand_total'],
                price_per_kg_inr=first_item.get('cost_per_kg', 0.0),
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                soil_ph=soil_ph,
                soil_type=soil_type,
                nutrient_analysis=plan['soil_summary'],
                nutrient_requirement=plan['nutrient_requirement'],
                nutrient_gap=plan['nutrient_gap'],
                application_schedule=plan['selected_plan_schedule'],
                alternative_fertilizers=plan['top_fertilizer_plans'],
                protection_plan=plan['protection_plan'],
                weather_snapshot=plan['weather_advisory'],
                cost_summary=plan['cost_summary'],
                safety_warnings=[
                    "Wear protective gloves and mask during fertilizer and pesticide application.",
                    "Do not mix phosphatic fertilizers directly with zinc sulphate in the same spray tank.",
                    "Apply nitrogenous fertilizers when soil has adequate moisture to prevent volatilization.",
                    "Keep all agrochemicals out of reach of children and farm animals."
                ],
                ai_explanation=plan['ai_explanation']['full_explanation']
            )

            return Response({
                "success": True,
                "data": plan,
                "history_id": rec_history.id,
                "message": "Smart Crop Nutrition & Protection Plan generated successfully."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error in CropNutritionPlanView: {e}")
            return Response(
                {"success": False, "message": f"An error occurred while generating plan: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FertilizerRecommendView(APIView):
    """
    POST /api/fertilizer/recommend/
    Backward-compatible endpoint delegating to CropNutritionPlanView logic.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        planner_view = CropNutritionPlanView()
        planner_view.request = request
        planner_view.format_kw = self.format_kw
        return planner_view.post(request)


class FertilizerHistoryListView(generics.ListAPIView):
    """
    GET /api/fertilizer/history/
    Lists previous recommendation plans for the logged-in user.
    Optional query parameter: ?farm_id=123
    """
    serializer_class = FertilizerRecommendationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = FertilizerRecommendationHistory.objects.filter(user=self.request.user)
        farm_id = self.request.query_params.get('farm_id')
        if farm_id:
            qs = qs.filter(farm_id=farm_id)
        return qs.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "count": queryset.count(),
            "data": serializer.data
        })

    def delete(self, request, *args, **kwargs):
        history_id = request.query_params.get('id') or request.data.get('id')
        if not history_id:
            return Response({"success": False, "error": "History ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = FertilizerRecommendationHistory.objects.get(pk=history_id, user=request.user)
            item.delete()
            return Response({"success": True, "message": "Recommendation history entry deleted successfully."})
        except FertilizerRecommendationHistory.DoesNotExist:
            return Response({"success": False, "error": "History record not found."}, status=status.HTTP_404_NOT_FOUND)


class FertilizerHistoryDetailView(APIView):
    """
    DELETE /api/fertilizer/history/<pk>/
    Deletes a specific fertilizer recommendation history record for the logged-in user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            item = FertilizerRecommendationHistory.objects.get(pk=pk, user=request.user)
            item.delete()
            return Response({"success": True, "message": "Recommendation history entry deleted successfully."})
        except FertilizerRecommendationHistory.DoesNotExist:
            return Response({"success": False, "error": "History record not found."}, status=status.HTTP_404_NOT_FOUND)



class FertilizerMasterListView(APIView):
    """
    GET /api/fertilizer/master/
    Returns the complete master catalog of fertilizers.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        catalog = load_fertilizer_master()
        return Response({
            "success": True,
            "count": len(catalog),
            "data": catalog
        })


class CropListView(APIView):
    """
    GET /api/fertilizer/crops/
    Returns list of all supported crops from dataset.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        crops = load_crop_list()
        return Response({
            "success": True,
            "count": len(crops),
            "data": crops
        })

