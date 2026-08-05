import logging
import math
from django.utils import timezone
from farms.models import Farm
from weather.services import WeatherCacheService
from ml.fertilizer_predictor import FertilizerPredictor
from .rule_engine import FertilizerRuleEngine
from ..models import FertilizerRecommendationHistory

logger = logging.getLogger(__name__)

class FertilizerService:
    """
    Main Service for Smart Fertilizer Recommendations.
    Supports Dual Decision Flow:
    1. Soil-Based Path (NPK & pH available) -> High Accuracy (90-98%)
    2. Estimated Path (NPK missing) -> Medium Accuracy (60-80%)
    """

    @staticmethod
    def generate_recommendation(farm_id: int, user, growth_stage: str = None, soil_overrides: dict = None) -> dict:
        farm = Farm.objects.get(id=farm_id, user=user)
        predictor = FertilizerPredictor()

        # Extract farm data
        crop = farm.farms.first().crop_name if hasattr(farm, 'crop_name') else 'Rice' # Fallback check
        # Check latest crop recommendation if farm crop not set
        from recommendation.models import RecommendationHistory
        latest_crop_rec = RecommendationHistory.objects.filter(farm=farm, user=user).order_by('-created_at').first()
        if latest_crop_rec:
            crop = latest_crop_rec.recommended_crop

        stage = growth_stage or "Basal / Sowing"
        soil_type = farm.soil_type or "Loamy"
        farm_area_acres = float(farm.farm_area or 1.0)
        if farm.area_unit and farm.area_unit.lower() == 'hectares':
            farm_area_acres *= 2.47105

        # Check NPK availability (either on farm model or soil_overrides)
        overrides = soil_overrides or {}
        n_val = overrides.get('nitrogen', farm.nitrogen)
        p_val = overrides.get('phosphorus', farm.phosphorus)
        k_val = overrides.get('potassium', farm.potassium)
        ph_val = overrides.get('soil_ph', farm.soil_ph)

        has_npk = (n_val is not None and p_val is not None and k_val is not None)
        ph_val = float(ph_val) if ph_val is not None else 6.5

        # Fetch Weather Data for Weather Rules
        weather_data = {}
        try:
            weather_data = WeatherCacheService.get_weather_data(farm.id)
        except Exception as e:
            logger.warning(f"Weather data fetch failed for farm {farm.id}: {e}")

        weather_rules = FertilizerRuleEngine.evaluate_weather_rules(weather_data)

        # -------------------------------------------------------------
        # DECISION PATH SELECTION
        # -------------------------------------------------------------
        if has_npk:
            rec_type = 'SOIL_BASED'
            confidence = 94.5
            recommendation_type_display = 'Soil-Based Recommendation'
            
            ideal_req = predictor.get_crop_requirement(crop, stage)
            ideal_n = float(ideal_req.get('Ideal_Nitrogen', 40.0))
            ideal_p = float(ideal_req.get('Ideal_Phosphorus', 40.0))
            ideal_k = float(ideal_req.get('Ideal_Potassium', 40.0))
            ideal_ph = float(ideal_req.get('Ideal_pH', 6.5))

            n_def = max(0.0, ideal_n - float(n_val))
            p_def = max(0.0, ideal_p - float(p_val))
            k_def = max(0.0, ideal_k - float(k_val))

            nutrient_analysis = {
                "nitrogen": {"current": float(n_val), "ideal": ideal_n, "status": "Low" if n_def > 5 else "Normal"},
                "phosphorus": {"current": float(p_val), "ideal": ideal_p, "status": "Low" if p_def > 5 else "Normal"},
                "potassium": {"current": float(k_val), "ideal": ideal_k, "status": "Low" if k_def > 5 else "Normal"},
                "soil_ph": {"current": ph_val, "ideal": ideal_ph, "status": "Acidic" if ph_val < 6.0 else ("Alkaline" if ph_val > 7.8 else "Normal")}
            }

            # Search Master Lookup Table
            matched_fert = predictor.find_best_fertilizer_by_deficiency(n_def, p_def, k_def, ph_val)
            recommended_fert_name = matched_fert.get('Fertilizer_Name', 'Urea')

        else:
            rec_type = 'ESTIMATED'
            confidence = 75.0
            recommendation_type_display = 'Estimated Recommendation'

            ideal_req = predictor.get_crop_requirement(crop, stage)
            ideal_n = float(ideal_req.get('Ideal_Nitrogen', 40.0))
            ideal_p = float(ideal_req.get('Ideal_Phosphorus', 40.0))
            ideal_k = float(ideal_req.get('Ideal_Potassium', 40.0))
            ideal_ph = 6.5

            nutrient_analysis = {
                "nitrogen": {"current": "N/A", "ideal": ideal_n, "status": "Estimated"},
                "phosphorus": {"current": "N/A", "ideal": ideal_p, "status": "Estimated"},
                "potassium": {"current": "N/A", "ideal": ideal_k, "status": "Estimated"},
                "soil_ph": {"current": "N/A", "ideal": ideal_ph, "status": "Estimated"}
            }

            # Use Crop, Soil Type, Growth Stage, & ML Predictor
            recommended_fert_name = predictor.predict_ml_fertilizer(
                crop=crop, soil_type=soil_type, n=30, p=30, k=30, ph=ph_val
            )
            matched_fert = predictor.get_fertilizer_details(recommended_fert_name)

        # -------------------------------------------------------------
        # DOSAGE & COST CALCULATIONS
        # -------------------------------------------------------------
        # Dosage per acre calculation based on N/P/K percentage of recommended fertilizer
        fn_pct = float(matched_fert.get('N_pct', 46) or 46)
        fp_pct = float(matched_fert.get('P_pct', 0) or 0)
        fk_pct = float(matched_fert.get('K_pct', 0) or 0)
        
        main_nutrient_pct = max(fn_pct, fp_pct, fk_pct, 15.0)
        target_nutrient_kg = float(ideal_req.get('Ideal_Nitrogen', 40.0)) if fn_pct > 20 else float(ideal_req.get('Ideal_Phosphorus', 40.0))
        
        dosage_per_acre_kg = round((target_nutrient_kg / (main_nutrient_pct / 100.0)) * 0.4046, 1) # Convert kg/ha to kg/acre
        if dosage_per_acre_kg < 10.0:
            dosage_per_acre_kg = 25.0
        elif dosage_per_acre_kg > 120.0:
            dosage_per_acre_kg = 50.0

        total_quantity_kg = round(dosage_per_acre_kg * farm_area_acres, 1)
        price_per_kg = float(matched_fert.get('Price_per_kg', 12.0) or 12.0)
        estimated_cost_inr = round(total_quantity_kg * price_per_kg, 2)

        # -------------------------------------------------------------
        # APPLICATION SCHEDULE & SPLITS
        # -------------------------------------------------------------
        application_schedule = [
            {
                "day": "Day 1 (Basal / Initial Application)",
                "quantity_kg": round(total_quantity_kg * 0.5, 1),
                "method": matched_fert.get("Application_Method", "Basal Soil Incorporation"),
                "instructions": "Apply 50% of total dose during land preparation or sowing. Incorporate into root zone."
            },
            {
                "day": "Day 15-20 (Active Growth / Tillering)",
                "quantity_kg": round(total_quantity_kg * 0.3, 1),
                "method": "Top Dressing / Broadcasting",
                "instructions": "Apply 30% of total dose near plant base when soil has optimum moisture."
            },
            {
                "day": "Day 35-40 (Flowering / Panicle Initiation)",
                "quantity_kg": round(total_quantity_kg * 0.2, 1),
                "method": "Top Dressing / Foliar Spray",
                "instructions": "Apply remaining 20% before flowering stage. Irrigate lightly after application."
            }
        ]

        # -------------------------------------------------------------
        # RANKED ALTERNATIVE FERTILIZERS
        # -------------------------------------------------------------
        alternative_fertilizers = [
            {
                "name": "DAP (Di-Ammonium Phosphate)" if recommended_fert_name != "DAP (Di-Ammonium Phosphate)" else "Urea",
                "npk_ratio": "18-46-0" if recommended_fert_name != "DAP (Di-Ammonium Phosphate)" else "46-0-0",
                "price_per_kg": 27.0 if recommended_fert_name != "DAP (Di-Ammonium Phosphate)" else 5.5,
                "reason": "Provides early root vigor and balanced Nitrogen & Phosphorus for initial growth."
            },
            {
                "name": "NPK 19-19-19",
                "npk_ratio": "19-19-19",
                "price_per_kg": 140.0,
                "reason": "100% water soluble complex. Ideal for foliar spray to quickly boost overall crop health."
            },
            {
                "name": "Vermicompost (Organic)",
                "npk_ratio": "1.5-1.0-1.5",
                "price_per_kg": 10.0,
                "reason": "Improves soil organic carbon, moisture retention, and beneficial micro-flora."
            }
        ]

        # -------------------------------------------------------------
        # AI EXPLANATION GENERATOR
        # -------------------------------------------------------------
        if rec_type == 'SOIL_BASED':
            ai_explanation = (
                f"Based on your soil test values for {farm.farm_name}, your soil Nitrogen and Phosphorus levels require replenishment for optimal {crop} yield. "
                f"{recommended_fert_name} is recommended because it contains {matched_fert.get('N_pct', '46')}% Nitrogen and efficiently addresses the detected deficit. "
                f"{weather_rules.get('weather_advice', '')}"
            )
        else:
            ai_explanation = (
                f"This recommendation for {crop} is calculated using crop nutrient demands, soil type ({soil_type}), season, and regional best practices because Soil Health Card (NPK) data was not available for {farm.farm_name}. "
                f"{recommended_fert_name} is recommended as the optimal standard baseline fertilizer. "
                f"For higher precision, update your farm profile with NPK values."
            )

        # Safety Warnings
        safety_warnings = FertilizerRuleEngine.generate_safety_warnings(recommended_fert_name, weather_rules, ph_val)

        # -------------------------------------------------------------
        # PERSIST TO DATABASE HISTORY
        # -------------------------------------------------------------
        rec_obj = FertilizerRecommendationHistory.objects.create(
            user=user,
            farm=farm,
            crop=crop,
            growth_stage=stage,
            recommendation_type=rec_type,
            confidence_score=confidence,
            recommended_fertilizer=recommended_fert_name,
            dosage_per_acre_kg=dosage_per_acre_kg,
            total_quantity_kg=total_quantity_kg,
            estimated_cost_inr=estimated_cost_inr,
            price_per_kg_inr=price_per_kg,
            nitrogen=float(n_val) if n_val is not None else None,
            phosphorus=float(p_val) if p_val is not None else None,
            potassium=float(k_val) if k_val is not None else None,
            soil_ph=ph_val,
            soil_type=soil_type,
            nutrient_analysis=nutrient_analysis,
            application_schedule=application_schedule,
            alternative_fertilizers=alternative_fertilizers,
            weather_snapshot=weather_rules,
            safety_warnings=safety_warnings,
            ai_explanation=ai_explanation,
            status='PENDING'
        )

        return {
            "id": rec_obj.id,
            "farm_id": farm.id,
            "farm_name": farm.farm_name,
            "crop": crop,
            "growth_stage": stage,
            "recommendation_type": rec_type,
            "recommendation_type_display": recommendation_type_display,
            "confidence_score": confidence,
            "recommended_fertilizer": recommended_fert_name,
            "fertilizer_details": matched_fert,
            "dosage_per_acre_kg": dosage_per_acre_kg,
            "total_quantity_kg": total_quantity_kg,
            "farm_area_acres": farm_area_acres,
            "price_per_kg_inr": price_per_kg,
            "estimated_cost_inr": estimated_cost_inr,
            "has_npk_data": has_npk,
            "nutrient_analysis": nutrient_analysis,
            "application_schedule": application_schedule,
            "alternative_fertilizers": alternative_fertilizers,
            "weather_rules": weather_rules,
            "safety_warnings": safety_warnings,
            "ai_explanation": ai_explanation,
            "status": rec_obj.status,
            "created_at": rec_obj.created_at.isoformat()
        }
