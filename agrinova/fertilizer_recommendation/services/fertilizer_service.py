import logging
import math
from django.utils import timezone
from farms.models import Farm
from weather.services import WeatherCacheService
from ml.fertilizer_predictor import FertilizerPredictor
from .rule_engine import FertilizerRuleEngine
from ..models import FertilizerRecommendationHistory

logger = logging.getLogger(__name__)

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
    Utilizes multi-criteria dataset filtering across 53 fertilizer products.
    """

    @staticmethod
    def generate_recommendation(farm_id: int, user, growth_stage: str = None, soil_overrides: dict = None, crop: str = None) -> dict:
        farm = Farm.objects.get(id=farm_id, user=user)
        predictor = FertilizerPredictor()

        # Extract farm data & determine crop
        overrides = soil_overrides or {}
        selected_crop = crop or overrides.get('crop')
        
        if not selected_crop:
            if hasattr(farm, 'crop_name') and getattr(farm, 'crop_name'):
                selected_crop = getattr(farm, 'crop_name')
            else:
                from recommendation.models import RecommendationHistory
                latest_crop_rec = RecommendationHistory.objects.filter(farm=farm, user=user).order_by('-created_at').first()
                if latest_crop_rec and latest_crop_rec.recommended_crop:
                    selected_crop = latest_crop_rec.recommended_crop
                else:
                    selected_crop = 'Rice'

        crop = selected_crop
        stage = growth_stage or "Basal / Sowing"
        soil_type = farm.soil_type or "Loamy"
        irrigation_type = getattr(farm, 'irrigation_type', '') or 'Drip'
        water_availability = getattr(farm, 'water_availability', '') or 'Good'
        
        # Respect original area unit
        farm_area_orig = float(farm.farm_area or 1.0)
        area_unit_orig = str(farm.area_unit or 'Acres').strip()
        farm_area_acres = FertilizerRuleEngine.convert_area_to_acres(farm_area_orig, area_unit_orig)

        # Check NPK availability (either on farm model or soil_overrides)
        n_val = overrides.get('nitrogen', farm.nitrogen)
        p_val = overrides.get('phosphorus', farm.phosphorus)
        k_val = overrides.get('potassium', farm.potassium)
        ph_val = overrides.get('soil_ph', farm.soil_ph)

        has_npk = (n_val is not None and p_val is not None and k_val is not None)
        try:
            ph_val = float(ph_val) if ph_val is not None else 6.5
        except (ValueError, TypeError):
            ph_val = 6.5

        # Fetch Weather Data for Weather Rules
        weather_data = {}
        try:
            weather_data = WeatherCacheService.get_weather_data(farm.id)
        except Exception as e:
            logger.warning(f"Weather data fetch failed for farm {farm.id}: {e}")

        weather_rules = FertilizerRuleEngine.evaluate_weather_rules(weather_data)

        # -------------------------------------------------------------
        # DECISION PATH SELECTION & NUTRIENT DEFICIT CALCULATION
        # -------------------------------------------------------------
        ideal_req = predictor.get_crop_requirement(crop, stage)
        try:
            ideal_n = float(ideal_req.get('Ideal_Nitrogen', 40.0))
            ideal_p = float(ideal_req.get('Ideal_Phosphorus', 40.0))
            ideal_k = float(ideal_req.get('Ideal_Potassium', 40.0))
            ideal_ph = float(ideal_req.get('Ideal_pH', 6.5))
        except (ValueError, TypeError):
            ideal_n, ideal_p, ideal_k, ideal_ph = 40.0, 40.0, 40.0, 6.5

        if has_npk:
            rec_type = 'SOIL_BASED'
            confidence = 94.5
            recommendation_type_display = 'Soil-Based Recommendation'
            
            try:
                n_def = max(0.0, ideal_n - float(n_val))
                p_def = max(0.0, ideal_p - float(p_val))
                k_def = max(0.0, ideal_k - float(k_val))
            except (ValueError, TypeError):
                n_def, p_def, k_def = 10.0, 10.0, 10.0

            nutrient_analysis = {
                "nitrogen": {"current": float(n_val), "ideal": ideal_n, "status": "Low" if n_def > 5 else ("High" if float(n_val) > ideal_n + 15 else "Normal")},
                "phosphorus": {"current": float(p_val), "ideal": ideal_p, "status": "Low" if p_def > 5 else ("High" if float(p_val) > ideal_p + 15 else "Normal")},
                "potassium": {"current": float(k_val), "ideal": ideal_k, "status": "Low" if k_def > 5 else ("High" if float(k_val) > ideal_k + 15 else "Normal")},
                "soil_ph": {"current": ph_val, "ideal": ideal_ph, "status": "Acidic" if ph_val < 6.0 else ("Alkaline" if ph_val > 7.8 else "Normal")}
            }

        else:
            rec_type = 'ESTIMATED'
            confidence = 75.0
            recommendation_type_display = 'Estimated Recommendation'
            n_def, p_def, k_def = 25.0, 25.0, 25.0

            nutrient_analysis = {
                "nitrogen": {"current": "N/A", "ideal": ideal_n, "status": "Estimated"},
                "phosphorus": {"current": "N/A", "ideal": ideal_p, "status": "Estimated"},
                "potassium": {"current": "N/A", "ideal": ideal_k, "status": "Estimated"},
                "soil_ph": {"current": "N/A", "ideal": ideal_ph, "status": "Estimated"}
            }

        # -------------------------------------------------------------
        # MULTI-CRITERIA DATASET SELECTION & TOP 4-5 RECOMMENDATIONS
        # -------------------------------------------------------------
        scored_candidates = predictor.get_top_recommendations_with_scores(
            crop=crop, growth_stage=stage,
            n_def=n_def, p_def=p_def, k_def=k_def,
            soil_ph=ph_val, soil_type=soil_type,
            water_availability=water_availability,
            irrigation_type=irrigation_type,
            top_k=5
        )

        top_recommendations = []
        for idx, cand in enumerate(scored_candidates):
            fn_pct = cand['N_pct']
            fp_pct = cand['P_pct']
            fk_pct = cand['K_pct']
            price = cand['price_per_kg']

            main_nutrient_pct = max(fn_pct, fp_pct, fk_pct, 15.0)
            target_nutrient_kg = ideal_n if fn_pct > 20 else (ideal_p if fp_pct > 20 else 30.0)

            # Compute dosage
            dosage_acre = round((target_nutrient_kg / (main_nutrient_pct / 100.0)) * 0.4046, 1)
            dosage_acre = max(10.0, min(120.0, dosage_acre))
            tot_kg = round(dosage_acre * farm_area_acres, 1)
            tot_cost = round(tot_kg * price, 2)

            unit_info = FertilizerRuleEngine.format_unit_dosage(tot_kg, farm_area_orig, area_unit_orig)

            top_recommendations.append({
                "rank": idx + 1,
                "name": cand['name'],
                "fertilizer_type": cand['fertilizer_type'],
                "npk_ratio": cand['npk_ratio'],
                "price_per_kg": price,
                "dosage_per_acre_kg": dosage_acre,
                "dosage_per_unit": unit_info['dosage_per_unit'],
                "dosage_per_unit_text": unit_info['dosage_per_unit_text'],
                "total_quantity_kg": tot_kg,
                "total_quantity_text": unit_info['total_quantity_text'],
                "estimated_cost_inr": tot_cost,
                "application_method": cand['application_method'],
                "why_recommended": cand['why_recommended'],
                "nutrients_supplied": cand['nutrients_supplied'],
                "suitability_score": cand['suitability_score']
            })

        # Primary recommendation is Top #1
        primary_rec = top_recommendations[0] if top_recommendations else {
            "name": "Urea", "dosage_per_acre_kg": 45.0, "total_quantity_kg": 45.0 * farm_area_acres,
            "estimated_cost_inr": 250.0, "price_per_kg": 5.5, "application_method": "Basal Incorporation",
            "suitability_score": 90.0
        }

        recommended_fert_name = primary_rec["name"]
        matched_fert = predictor.get_fertilizer_details(recommended_fert_name)
        dosage_per_acre_kg = primary_rec["dosage_per_acre_kg"]
        total_quantity_kg = primary_rec["total_quantity_kg"]
        estimated_cost_inr = primary_rec["estimated_cost_inr"]
        price_per_kg = float(primary_rec.get("price_per_kg", matched_fert.get("Price_per_kg", 15.0)))
        confidence = float(primary_rec.get("suitability_score", 94.5))

        # Dynamic alternative list (Top #2 through #5)
        alternative_fertilizers = []
        for alt in top_recommendations[1:]:
            alternative_fertilizers.append({
                "name": alt["name"],
                "npk_ratio": alt["npk_ratio"],
                "price_per_kg": alt["price_per_kg"],
                "reason": alt["why_recommended"],
                "suitability_score": alt["suitability_score"],
                "total_quantity_kg": alt["total_quantity_kg"],
                "dosage_per_unit": alt["dosage_per_unit_text"],
                "application_method": alt["application_method"]
            })

        # -------------------------------------------------------------
        # APPLICATION SCHEDULE & SPLITS
        # -------------------------------------------------------------
        application_schedule = [
            {
                "day": "Day 1 (Basal / Initial Application)",
                "quantity_kg": round(total_quantity_kg * 0.5, 1),
                "method": matched_fert.get("Application_Method", "Basal Soil Incorporation"),
                "instructions": f"Apply 50% of total dose during land preparation or sowing. Incorporate into root zone."
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
        # AI EXPLANATION GENERATOR
        # -------------------------------------------------------------
        fn_pct = matched_fert.get('N_pct', '0')
        fp_pct = matched_fert.get('P_pct', '0')
        fk_pct = matched_fert.get('K_pct', '0')

        if rec_type == 'SOIL_BASED':
            ai_explanation = (
                f"Based on soil test values for {farm.farm_name}, {recommended_fert_name} was dynamically selected as the most suitable fertilizer for your {crop} crop on {soil_type} soil. "
                f"It supplies NPK ({fn_pct}-{fp_pct}-{fk_pct}) targeting your specific nutrient deficits. "
                f"{weather_rules.get('weather_advice', '')}"
            )
        else:
            ai_explanation = (
                f"This recommendation for {crop} is calculated using crop nutrient demands, soil type ({soil_type}), water availability ({water_availability}), and regional best practices because Soil Health Card (NPK) data was not provided for {farm.farm_name}. "
                f"{recommended_fert_name} is recommended as the optimal standard fertilizer. "
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

        unit_info = FertilizerRuleEngine.format_unit_dosage(total_quantity_kg, farm_area_orig, area_unit_orig)

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
            "dosage_per_unit": unit_info["dosage_per_unit"],
            "dosage_per_unit_text": unit_info["dosage_per_unit_text"],
            "total_quantity_kg": total_quantity_kg,
            "total_quantity_text": unit_info["total_quantity_text"],
            "farm_area_original": farm_area_orig,
            "area_unit": area_unit_orig,
            "farm_area_acres": farm_area_acres,
            "price_per_kg_inr": price_per_kg,
            "estimated_cost_inr": estimated_cost_inr,
            "has_npk_data": has_npk,
            "nutrient_analysis": nutrient_analysis,
            "application_schedule": application_schedule,
            "alternative_fertilizers": alternative_fertilizers,
            "top_recommendations": top_recommendations,
            "weather_rules": weather_rules,
            "safety_warnings": safety_warnings,
            "ai_explanation": ai_explanation,
            "status": rec_obj.status,
            "created_at": rec_obj.created_at.isoformat()
        }

