from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from farms.models import Farm
from recommendation.models import RecommendationHistory
from market_forecast.services.market_cache_service import MarketCacheService
from ml.market_model_manager import MarketModelManager
from ml.model_manager import ModelManager
from recommendation.season.season_service import determine_season
from recommendation.weather.weather_service import fetch_current_weather

from .services.cost_loader import CostLoaderService
from .services.profit_engine import ProfitEngine
from .models import ProfitAnalysisHistory

class ProfitAnalysisView(APIView):
    """
    Main API endpoint for Profit Analysis module.
    Automatically combines:
    - Farm data
    - Crop Recommendation / Yield Prediction
    - Weather Cache
    - Market Intelligence / Market Prediction (3-month predicted price)
    - Cost Dataset (CACP / DES government averages)
    - Temporary Cost Object with custom cost overrides support
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self._process_profit_analysis(request, request.data)

    def get(self, request):
        return self._process_profit_analysis(request, request.query_params)

    def _process_profit_analysis(self, request, params):
        farm_id = params.get('farm_id')
        rec_id = params.get('rec_id')
        requested_crop = params.get('crop')
        custom_costs = params.get('custom_costs')

        if not farm_id:
            return Response({"success": False, "error": "farm_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            farm = Farm.objects.get(id=farm_id, user=request.user)
        except Farm.DoesNotExist:
            return Response({"success": False, "error": "Farm not found."}, status=status.HTTP_404_NOT_FOUND)

        # 1. Fetch Recommendation History
        rec_history = None
        if rec_id:
            rec_history = RecommendationHistory.objects.filter(id=rec_id, user=request.user).first()
        if not rec_history:
            rec_history = RecommendationHistory.objects.filter(farm=farm, user=request.user).order_by('-created_at').first()

        # 2. Determine target crop
        if requested_crop:
            target_crop = requested_crop.strip().title()
        elif rec_history:
            target_crop = rec_history.recommended_crop.strip().title()
        else:
            target_crop = "Cotton" # Default fallback crop

        state = farm.state or "Gujarat"
        district = farm.district or "Rajkot"

        # 3. Fetch MarketCache and 3-Month Market Prediction Price
        market_cache = MarketCacheService.get_or_fetch_market_cache(target_crop, state, district)
        current_price_info = market_cache.current_price or {}
        history_records = market_cache.yearly_price_history or market_cache.monthly_price_history or market_cache.weekly_price_history or []

        predicted_3m_price = 0.0
        try:
            market_predictor = MarketModelManager.get_instance().get_predictor()
            pred_output = market_predictor.predict_market_intelligence(current_price_info, history_records)
            medium_term = pred_output.get("medium_term_months", [])
            if len(medium_term) >= 3:
                predicted_3m_price = float(medium_term[2].get("predicted_avg_price", 0.0))
            elif len(medium_term) > 0:
                predicted_3m_price = float(medium_term[0].get("predicted_avg_price", 0.0))
        except Exception:
            pass

        if predicted_3m_price <= 0:
            predicted_3m_price = float(current_price_info.get("modal_price") or 4500.0)

        # 4. Determine Expected Yield in Quintals (Total for farm)
        from recommendation.views import get_area_unit_info
        farm_area_val = float(farm.farm_area or 1.0)
        unit_info = get_area_unit_info(farm_area_val, farm.area_unit)
        ha_per_unit = unit_info["ha_per_unit"]

        if rec_history and rec_history.recommended_crop.strip().lower() == target_crop.lower():
            exp_yield_kg_ha = float(rec_history.expected_yield or 4000.0)
        else:
            # Predict yield for custom crop using ML predictor
            weather_data = fetch_current_weather(farm.latitude, farm.longitude)
            season = determine_season()
            feature_dict = {
                "nitrogen": float(farm.nitrogen if farm.nitrogen is not None else 80.0),
                "phosphorus": float(farm.phosphorus if farm.phosphorus is not None else 45.0),
                "potassium": float(farm.potassium if farm.potassium is not None else 40.0),
                "ph": float(farm.soil_ph if farm.soil_ph is not None else 6.5),
                "temperature": float(weather_data.get('temperature', 26.5) or 26.5),
                "humidity": float(weather_data.get('humidity', 65.0) or 65.0),
                "rainfall": float(weather_data.get('rainfall', 120.0) or 120.0),
                "season": season,
                "soil_type": farm.soil_type or "Loam",
                "water_availability": farm.water_availability or "Medium"
            }
            try:
                model_mgr = ModelManager.get_instance()
                predictor = model_mgr.get_predictor()
                exp_yield_kg_ha = float(predictor.predict_yield(target_crop, feature_dict))
            except Exception:
                exp_yield_kg_ha = 4200.0

        yield_per_unit = (exp_yield_kg_ha * ha_per_unit) / 100.0 # Quintal per unit area
        total_yield_quintals = round(yield_per_unit * farm_area_val, 2)

        # 5. Load Cost Dataset for Crop + State
        base_cost_dict = CostLoaderService.get_crop_cost(target_crop, state)

        # 6. Execute Profit Engine calculation using Temporary Cost Object
        analysis_res = ProfitEngine.calculate_profit_analysis(
            farm=farm,
            crop=target_crop,
            expected_yield_total_quintals=total_yield_quintals,
            predicted_market_price=predicted_3m_price,
            base_cost_dict=base_cost_dict,
            custom_cost_overrides=custom_costs
        )

        # Save history log record
        try:
            ProfitAnalysisHistory.objects.create(
                user=request.user,
                farm=farm,
                recommendation_history=rec_history,
                crop=target_crop,
                state=state,
                farm_area=farm_area_val,
                area_unit=analysis_res["farm_info"]["farm_area_unit"],
                expected_yield_total=total_yield_quintals,
                predicted_market_price=predicted_3m_price,
                cost_breakdown=analysis_res["cost_breakdown"],
                financial_summary=analysis_res["financial_summary"],
                scenarios=analysis_res["scenarios"],
                risk_analysis=analysis_res["risk_analysis"]
            )
        except Exception as e:
            print(f"[ProfitAnalysisHistory Save Error]: {e}")

        return Response({
            "success": True,
            "data": analysis_res
        }, status=status.HTTP_200_OK)
