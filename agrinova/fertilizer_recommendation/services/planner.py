"""
Crop Nutrition Planner — Master orchestrator for the Smart Crop Nutrition & Protection Planner.
Combines Soil Analysis, Crop Nutrient Gap, LP Optimizer (Budget, Balanced, Premium Plans),
Crop Protection Planner, Weather Advisory, Split Schedule, Cost Engine, and AI Explanation into a unified plan object.
"""

import logging
from .area_converter import to_hectares
from .soil_analyzer import get_soil_summary
from .nutrient_planner import get_crop_requirement, compute_nutrient_gap
from .fertilizer_optimizer import generate_optimized_plans
from .protection_planner import generate_protection_plan
from .weather_advisor import get_weather_for_farm, generate_weather_advisory
from .cost_engine import calculate_plan_cost, calculate_protection_cost, calculate_grand_total
from .schedule_engine import generate_split_schedule
from .explanation_engine import generate_ai_explanation

logger = logging.getLogger(__name__)


class CropNutritionPlanner:
    """
    Production-ready master planner for Smart Crop Nutrition & Protection.
    """

    @classmethod
    def generate_plan(cls, crop: str, farm_area: float = 1.0, area_unit: str = 'Acres',
                      soil_type: str = 'Loamy', state: str = 'Punjab', season: str = 'Kharif',
                      previous_crop: str = '', farm_id: int = None,
                      nitrogen: float = None, phosphorus: float = None, potassium: float = None,
                      soil_ph: float = None, sulphur: float = None, calcium: float = None,
                      magnesium: float = None, zinc: float = None, boron: float = None,
                      iron: float = None, manganese: float = None, copper: float = None,
                      organic_carbon: float = None, electrical_conductivity: float = None,
                      soil_moisture: float = None) -> dict:
        """
        Main entry point. Computes complete nutrition & protection plan.
        """
        farm_area = max(0.1, float(farm_area or 1.0))
        area_unit = (area_unit or 'Acres').strip()
        crop_clean = (crop or 'Wheat').strip()
        soil_type_clean = (soil_type or 'Loamy').strip()
        state_clean = (state or 'Punjab').strip()
        season_clean = (season or 'Kharif').strip()

        # 1. Soil Analysis & Source Resolution
        soil_analysis = get_soil_summary(
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
            soil_moisture=soil_moisture,
            soil_type=soil_type_clean,
            state=state_clean,
            season=season_clean,
            previous_crop=previous_crop
        )
        soil_nutrients = soil_analysis['soil_nutrients']
        sources_map = soil_analysis.get('nutrient_sources', {})
        classifications_map = soil_analysis.get('nutrient_classifications', {})

        # 2. Crop Requirement & Nutrient Gap
        crop_req = get_crop_requirement(crop_clean, season_clean)
        nutrient_gap = compute_nutrient_gap(crop_req, soil_nutrients)

        # Deficits
        n_def = nutrient_gap['N']['deficit']
        p_def = nutrient_gap['P']['deficit']
        k_def = nutrient_gap['K']['deficit']

        # Construct Farmer-Friendly Nutrient Analysis Matrix
        nutrient_matrix = {}
        nutrient_definitions = [
            ('Nitrogen', 'N', 'kg/ha', crop_req.get('N', 0), soil_nutrients.get('N', 0), nutrient_gap['N']),
            ('Phosphorus (P₂O₅)', 'P', 'kg/ha', crop_req.get('P', 0), soil_nutrients.get('P', 0), nutrient_gap['P']),
            ('Potassium (K₂O)', 'K', 'kg/ha', crop_req.get('K', 0), soil_nutrients.get('K', 0), nutrient_gap['K']),
            ('Sulphur (S)', 'S', 'kg/ha', crop_req.get('S', 0), soil_nutrients.get('S', 0), nutrient_gap.get('S', {})),
            ('Zinc (Zn)', 'Zn', 'ppm', crop_req.get('Zn', 0), soil_nutrients.get('Zn', 0), nutrient_gap.get('Zn', {})),
            ('Boron (B)', 'B', 'ppm', crop_req.get('B', 0), soil_nutrients.get('B', 0), nutrient_gap.get('B', {})),
            ('Calcium (Ca)', 'Ca', 'kg/ha', 0, soil_nutrients.get('Ca', 0), {}),
            ('Magnesium (Mg)', 'Mg', 'kg/ha', 0, soil_nutrients.get('Mg', 0), {}),
            ('Organic Carbon', 'OC', '%', 0.75, soil_nutrients.get('OC', 0), {}),
            ('Soil pH', 'pH', 'pH', 7.0, soil_nutrients.get('pH', 7.0), {}),
        ]

        for label, key, unit, req_val, avail_val, gap_dict in nutrient_definitions:
            status = gap_dict.get('status', 'Adequate') if gap_dict else 'Adequate'
            deficit = gap_dict.get('deficit', 0.0) if gap_dict else 0.0
            
            # Action recommendation logic
            if deficit > 0:
                action = f"Apply {deficit} {unit} to satisfy crop requirement"
            elif status == 'Excess':
                action = "Adequate soil reserves — avoid excess application"
            else:
                action = "Maintain optimal soil fertility levels"

            nutrient_matrix[key] = {
                'label': label,
                'key': key,
                'unit': unit,
                'classification': classifications_map.get(key, 'Medium'),
                'crop_requirement': req_val,
                'available_nutrient': avail_val,
                'deficit': deficit,
                'status': status,
                'recommended_action': action,
                'source': sources_map.get(key, soil_analysis.get('source', 'Estimated')),
            }

        # 3. Weather Data & Advisory
        weather_data = {}
        if farm_id:
            weather_data = get_weather_for_farm(farm_id)
        weather_advisory = generate_weather_advisory(weather_data)

        # 4. Generate Top Optimized Plans (Budget, Balanced, Premium)
        raw_plans = generate_optimized_plans(
            target_n=n_def,
            target_p=p_def,
            target_k=k_def,
            crop=crop_clean,
            soil_type=soil_type_clean,
            season=season_clean,
            soil_ph=soil_nutrients.get('pH', 7.0),
            max_plans=3
        )

        # Process each multi-plan with costs & schedules
        processed_plans = []
        for p in raw_plans:
            cost_info = calculate_plan_cost(p['items'], farm_area, area_unit)
            schedule = generate_split_schedule(crop_clean, p['items'], farm_area, area_unit)

            processed_plans.append({
                'title': p['title'],
                'description': p['description'],
                'tag': p['tag'],
                'strategy': p['strategy'],
                'badge_color': p.get('badge_color', 'emerald'),
                'advantages': p.get('advantages', []),
                'score': p['score'],
                'cost': cost_info,
                'items': cost_info.get('items', []),
                'split_schedule': schedule,
            })

        # Primary (Selected) Plan
        selected_plan = processed_plans[1] if len(processed_plans) > 1 else (processed_plans[0] if processed_plans else {})
        selected_raw_plan = raw_plans[1] if len(raw_plans) > 1 else (raw_plans[0] if raw_plans else {'items': []})

        # 5. Crop Protection Plan
        protection_plan = generate_protection_plan(crop_clean, weather_data)

        # 6. Complete Cost Summary Breakdown
        nutrition_cost = selected_plan.get('cost', {'total_cost': 0.0})
        protection_cost = calculate_protection_cost(protection_plan, farm_area, area_unit)
        cost_summary = calculate_grand_total(nutrition_cost, protection_cost, farm_area, area_unit)

        # 7. AI Explanation
        ai_explanation = generate_ai_explanation(
            crop=crop_clean,
            soil_summary=soil_analysis,
            nutrient_gap=nutrient_gap,
            selected_plan=selected_raw_plan,
            protection_plan=protection_plan,
            weather_advisory=weather_advisory
        )

        return {
            'crop_summary': {
                'crop': crop_clean,
                'farm_area': farm_area,
                'area_unit': area_unit,
                'area_display': f"{farm_area} {area_unit}",
                'area_in_hectares': to_hectares(farm_area, area_unit),
                'soil_type': soil_type_clean,
                'state': state_clean,
                'season': season_clean,
                'previous_crop': previous_crop or 'None',
            },
            'soil_summary': soil_analysis,
            'nutrient_matrix': nutrient_matrix,
            'nutrient_requirement': crop_req,
            'nutrient_gap': nutrient_gap,
            'top_fertilizer_plans': processed_plans,
            'selected_plan_schedule': selected_plan.get('split_schedule', []),
            'protection_plan': protection_plan,
            'weather_advisory': weather_advisory,
            'cost_summary': cost_summary,
            'ai_explanation': ai_explanation,
        }
