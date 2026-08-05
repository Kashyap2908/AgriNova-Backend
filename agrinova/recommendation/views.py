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


def get_area_unit_info(farm_area: float, raw_unit: str):
    unit = str(raw_unit or 'Acre').strip()
    u_lower = unit.lower()

    if 'hectare' in u_lower or u_lower == 'ha':
        canonical_unit = 'Hectare'
        acres_per_unit = 2.47105
        ha_per_unit = 1.0
    elif 'bigha' in u_lower:
        canonical_unit = 'Bigha'
        acres_per_unit = 0.4
        ha_per_unit = 0.4 / 2.47105
    elif 'gunta' in u_lower:
        canonical_unit = 'Gunta'
        acres_per_unit = 0.025
        ha_per_unit = 0.025 / 2.47105
    elif 'kanal' in u_lower:
        canonical_unit = 'Kanal'
        acres_per_unit = 0.125
        ha_per_unit = 0.125 / 2.47105
    elif 'marla' in u_lower:
        canonical_unit = 'Marla'
        acres_per_unit = 0.00625
        ha_per_unit = 0.00625 / 2.47105
    elif 'biswa' in u_lower:
        canonical_unit = 'Biswa'
        acres_per_unit = 0.02
        ha_per_unit = 0.02 / 2.47105
    else:
        canonical_unit = 'Acre'
        acres_per_unit = 1.0
        ha_per_unit = 1.0 / 2.47105

    return {
        "display_unit": unit,
        "canonical_unit": canonical_unit,
        "acres_per_unit": acres_per_unit,
        "ha_per_unit": ha_per_unit,
        "yield_unit_label": f"Quintal/{unit}"
    }


class YieldSummaryView(APIView):
    """
    Returns structured yield prediction analysis and inputs for Yield Prediction Module.
    Supports both Recommended Crop (top/multi recommendations) and Custom Crop selected manually.
    Preserves original farm area unit (Acre, Hectare, Bigha, Gunta, Kanal, etc.).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        params = getattr(request, 'data', getattr(request, 'POST', {}))
        return self._process_yield_summary(request, params)

    def get(self, request):
        params = getattr(request, 'query_params', getattr(request, 'GET', {}))
        return self._process_yield_summary(request, params)


    def _process_yield_summary(self, request, params):
        from recommendation.weather.weather_service import fetch_current_weather
        from recommendation.season.season_service import determine_season
        from ml.model_manager import ModelManager

        farm_id = params.get('farm_id')
        rec_id = params.get('rec_id')
        requested_crop = params.get('crop')

        # 1. Determine Farm
        farm = None
        if farm_id:
            farm = Farm.objects.filter(id=farm_id, user=request.user).first()
        if not farm:
            farm = Farm.objects.filter(user=request.user, is_active=True).first()
        if not farm:
            farm = Farm.objects.filter(user=request.user).first()

        if not farm:
            return Response({
                "success": False,
                "error": "No farm found. Please add a farm first."
            }, status=status.HTTP_404_NOT_FOUND)

        # 2. Fetch Recommendation History if available
        rec_history = None
        if rec_id:
            rec_history = RecommendationHistory.objects.filter(pk=rec_id, user=request.user).first()
        if not rec_history and farm:
            rec_history = RecommendationHistory.objects.filter(farm=farm, user=request.user).order_by('-created_at').first()

        # 3. Target Crop Determination
        if requested_crop:
            target_crop = requested_crop.strip().title()
        elif rec_history and rec_history.recommended_crop:
            target_crop = rec_history.recommended_crop.strip().title()
        else:
            season_temp = determine_season()
            available_crops = get_all_available_crops_for_farm(farm, season_temp)
            target_crop = available_crops[0] if available_crops else "Cotton"

        # 4. Fetch Weather & Farm Inputs
        weather = (rec_history.weather_snapshot if (rec_history and rec_history.weather_snapshot) else None) or fetch_current_weather(farm.latitude, farm.longitude)
        season = (rec_history.results_payload.get('season') if (rec_history and isinstance(rec_history.results_payload, dict)) else None) or determine_season()
        inputs = (rec_history.input_values if (rec_history and rec_history.input_values) else None) or {}


        # 5. Determine Expected Yield in kg/ha
        exp_yield_kg_ha = None
        if rec_history:
            if rec_history.recommended_crop and rec_history.recommended_crop.strip().lower() == target_crop.lower() and not requested_crop:
                exp_yield_kg_ha = float(rec_history.expected_yield or 0.0)

            if not exp_yield_kg_ha and rec_history.results_payload and isinstance(rec_history.results_payload, dict):
                recs_list = rec_history.results_payload.get('recommendations', [])
                for r in recs_list:
                    if r.get('crop', '').strip().lower() == target_crop.lower():
                        exp_yield_kg_ha = float(r.get('expected_yield', 0.0))
                        break
                if not exp_yield_kg_ha:
                    comps_list = rec_history.results_payload.get('comparison', [])
                    for c in comps_list:
                        if c.get('crop', '').strip().lower() == target_crop.lower():
                            exp_yield_kg_ha = float(c.get('expected_yield', 0.0))
                            break

        if not exp_yield_kg_ha or exp_yield_kg_ha <= 0:
            # Predict yield dynamically for custom crop or fallback
            feature_dict = {
                "nitrogen": float(inputs.get('nitrogen', farm.nitrogen or 80.0) or 80.0),
                "phosphorus": float(inputs.get('phosphorus', farm.phosphorus or 45.0) or 45.0),
                "potassium": float(inputs.get('potassium', farm.potassium or 40.0) or 40.0),
                "ph": float(inputs.get('soil_ph', farm.soil_ph or 6.5) or 6.5),
                "temperature": float(weather.get('temperature', 26.5) or 26.5),
                "humidity": float(weather.get('humidity', 65.0) or 65.0),
                "rainfall": float(weather.get('rainfall', 120.0) or 120.0),
                "season": season,
                "soil_type": farm.soil_type or "Loam",
                "water_availability": farm.water_availability or "Medium"
            }
            try:
                model_mgr = ModelManager.get_instance()
                predictor = model_mgr.get_predictor()
                exp_yield_kg_ha = float(predictor.predict_yield(target_crop, feature_dict))
            except Exception as e:
                import traceback
                print(f"[YieldSummaryView Dynamic Yield Error]: {traceback.format_exc()}")
                exp_yield_kg_ha = 4200.0

        # 6. Unit Conversion (Preserve Farmer's Original Area Unit)
        farm_area_val = float(farm.farm_area or 1.0)
        unit_info = get_area_unit_info(farm_area_val, farm.area_unit)

        displayed_unit = unit_info["display_unit"]
        yield_unit_label = unit_info["yield_unit_label"]
        ha_per_unit = unit_info["ha_per_unit"]

        # Yield per 1 unit of farm area (in Quintals)
        yield_per_unit = round((exp_yield_kg_ha * ha_per_unit) / 100.0, 2)
        total_expected_yield = round(yield_per_unit * farm_area_val, 2)

        # 7. Safe feature value extractions for insights
        ph_val = float(inputs.get('soil_ph', farm.soil_ph or 6.5) or 6.5)
        n_val = float(inputs.get('nitrogen', farm.nitrogen or 80.0) or 80.0)
        p_val = float(inputs.get('phosphorus', farm.phosphorus or 45.0) or 45.0)
        k_val = float(inputs.get('potassium', farm.potassium or 40.0) or 40.0)
        temp_val = float(weather.get('temperature', 26.5) or 26.5)
        humidity_val = float(weather.get('humidity', 65.0) or 65.0)
        rain_val = float(weather.get('rainfall', 120.0) or 120.0)

        if 6.0 <= ph_val <= 7.5 and n_val >= 50:
            soil_health = "Optimal (Balanced pH & Good Nutrient Content)"
        elif ph_val < 6.0:
            soil_health = "Slightly Acidic (Consider Lime Application)"
        else:
            soil_health = "Moderate Soil Health (Monitored N-P-K Levels)"

        if 18 <= temp_val <= 35 and rain_val >= 50:
            weather_suitability = "Highly Favorable (Ideal Thermal & Moisture Conditions)"
        else:
            weather_suitability = "Moderate Weather Suitability"

        water_avail_display = farm.water_availability if farm.water_availability else "Unknown"
        soil_type_display = farm.soil_type if farm.soil_type else "Unknown"

        if exp_yield_kg_ha >= 5000:
            yield_category = "High Yielding Potential"
        elif exp_yield_kg_ha >= 3000:
            yield_category = "Above Average Yielding Potential"
        else:
            yield_category = "Moderate Yielding Potential"

        expected_performance = f"Optimal growth anticipated for {target_crop} based on environmental and soil metrics."

        recommendations = [
            f"Maintain irrigation schedule suitable for {water_avail_display.lower()} water availability.",
            f"Monitor N-P-K levels, keeping Nitrogen at ~{n_val} kg/ha for target crop uptake.",
            f"Suitable crop ({target_crop}) evaluated for {season} season in {farm.state}.",
            "Avoid water stress during critical flowering and grain filling stages."
        ]

        recommendation_summary = None
        if rec_history and rec_history.results_payload and isinstance(rec_history.results_payload, dict):
            recommendation_summary = {
                "top_crop": rec_history.recommended_crop,
                "confidence": rec_history.confidence,
                "recommendations": rec_history.results_payload.get('recommendations', []),
                "mode": rec_history.recommendation_mode,
                "type": rec_history.recommendation_type
            }

        # Soil Health Card determination
        has_soil_report = bool(
            getattr(farm, 'last_soil_test_date', None) or 
            (rec_history and getattr(rec_history, 'recommendation_mode', '') == 'AI')
        )

        def get_nutrient_source(param_name, farm_val):
            if has_soil_report:
                return "Soil Health Card"
            if inputs.get(param_name) is not None or farm_val is not None:
                return "Farm Information"
            return "Estimated (No Soil Health Card)"

        n_source = get_nutrient_source('nitrogen', farm.nitrogen)
        p_source = get_nutrient_source('phosphorus', farm.phosphorus)
        k_source = get_nutrient_source('potassium', farm.potassium)
        ph_source = get_nutrient_source('soil_ph', farm.soil_ph)

        data = {
            "crop_info": {
                "farm_name": farm.farm_name,
                "selected_crop": target_crop,
                "state": farm.state,
                "district": farm.district,
                "season": season,
                "farm_area": farm_area_val,
                "farm_area_unit": displayed_unit,
                "has_recommendation": bool(rec_history),
                "recommendation_id": rec_history.id if rec_history else None
            },
            "recommendation_summary": recommendation_summary,
            "prediction_inputs": {
                "nitrogen": n_val,
                "phosphorus": p_val,
                "potassium": k_val,
                "temperature": temp_val,
                "humidity": humidity_val,
                "rainfall": rain_val,
                "ph": ph_val,
                "soil_type": soil_type_display,
                "water_availability": water_avail_display,
                "water_requirement": float(inputs.get('water_requirement', 1200) or 1200),
                "has_soil_health_card": has_soil_report,
                "input_sources": {
                    "nitrogen": n_source,
                    "phosphorus": p_source,
                    "potassium": k_source,
                    "ph": ph_source,
                    "temperature": "Weather Cache",
                    "humidity": "Weather Cache",
                    "rainfall": "Weather Cache",
                    "soil_type": "Farm Information" if farm.soil_type else "Not Provided",
                    "water_availability": "Farm Information" if farm.water_availability else "Not Provided",
                    "water_requirement": "Crop Dataset"
                }
            },
            "yield_prediction": {
                "yield_per_unit_area": yield_per_unit,
                "unit_label": yield_unit_label,
                "total_expected_yield": total_expected_yield,
                "total_unit_label": "Quintal",
                "raw_expected_yield_kg_ha": exp_yield_kg_ha
            },
            "yield_analysis": {
                "soil_health": soil_health,
                "weather_suitability": weather_suitability,
                "water_availability": water_avail_display,
                "yield_category": yield_category,
                "expected_performance": expected_performance
            },
            "recommendations": recommendations
        }


        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)


