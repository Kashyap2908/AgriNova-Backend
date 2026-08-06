"""
Master Fertilizer Recommendation Engine
Orchestrates the entire Hybrid AI Pipeline: Mode Selection -> Nutrient Estimation -> Optimizer -> Ranking -> Weather -> Cost -> Schedule -> AI Explanation.
"""

import logging
from .fertilizer_catalog import FertilizerCatalog
from .crop_requirement_engine import CropRequirementEngine
from .soil_estimation_engine import SoilEstimationEngine
from .deficiency_calculator import DeficiencyCalculator
from .candidate_generator import CandidateGenerator
from .combination_optimizer import CombinationOptimizer
from .ranking_engine import RankingEngine
from .rule_engine import AgronomicRuleEngine
from .weather_adjustment import WeatherAdjustmentEngine
from .cost_calculator import CostCalculator
from .schedule_generator import ScheduleGenerator
from .explanation_generator import ExplanationGenerator

logger = logging.getLogger(__name__)


class SmartFertilizerEngine:
    """
    Production-ready Smart Fertilizer Recommendation Master Engine.
    Powered by Linear Programming (Mathematical Optimization).
    """

    def generate_recommendation(self, farm_id: int = None, crop: str = '',
                                nitrogen: float = None, phosphorus: float = None, potassium: float = None,
                                ph: float = None, soil_type: str = 'Loamy', state: str = 'Punjab',
                                season: str = 'Kharif', farm_area: float = 1.0,
                                previous_crop: str = '', force_mode: str = None) -> dict:
        
        crop_clean = crop.strip() if crop else 'Wheat'
        soil_type_clean = soil_type.strip() if soil_type else 'Loamy'
        state_clean = state.strip() if state else 'Punjab'
        season_clean = season.strip() if season else 'Kharif'
        farm_area_val = max(0.1, float(farm_area or 1.0))
        prev_crop_clean = previous_crop.strip() if previous_crop else ''

        has_soil_card = (
            nitrogen is not None and phosphorus is not None and potassium is not None and
            float(nitrogen or 0) > 0 and float(phosphorus or 0) > 0 and float(potassium or 0) > 0
        )

        # STEP 1: Crop Requirement Engine
        ideal_req = CropRequirementEngine.get_ideal_requirements(crop_clean)

        # STEP 2: Soil Estimation Engine
        if has_soil_card:
            mode = 'PRECISION'
            soil_n = float(nitrogen)
            soil_p = float(phosphorus)
            soil_k = float(potassium)
            soil_ph = float(ph) if ph is not None and float(ph) > 0 else 7.0
        else:
            mode = 'SMART'
            est = SoilEstimationEngine.estimate_soil_nutrients(soil_type_clean, state_clean, season_clean, prev_crop_clean)
            soil_n = est['N']
            soil_p = est['P']
            soil_k = est['K']
            soil_ph = 7.0 # Default if unknown

        # STEP 3: Deficiency Calculator
        actual_soil = {'N': soil_n, 'P': soil_p, 'K': soil_k}
        deficiency = DeficiencyCalculator.calculate_deficiency(ideal_req, actual_soil)

        # STEP 4: Fertilizer Candidate Generator
        global_catalog = FertilizerCatalog.get_all_fertilizers()
        candidates = CandidateGenerator.generate_candidates(global_catalog, soil_ph)

        # STEP 5: Fertilizer Combination Optimizer (LP)
        plans = CombinationOptimizer.generate_all_plans(
            target_n=deficiency['N'],
            target_p=deficiency['P'],
            target_k=deficiency['K'],
            catalog=candidates
        )

        # STEP 6: Weather Engine
        weather_summary = {'condition': 'Normal', 'weather_advice': []}
        weather_adj = WeatherAdjustmentEngine.get_adjustment(weather_summary)
        
        if not plans:
            top_solution = {
                'title': 'No Synthetic Fertilizer Required',
                'description': 'Soil nutrient levels are optimal. No additional synthetic fertilizers are required at this stage.',
                'items': [],
                'score': 100.0,
                'tag': 'OPTIMAL',
                'strategy': 'optimal'
            }
            ranked_plans = [top_solution]
            primary_rec = top_solution
        else:
            # STEP 7: Ranking Engine
            ranked_plans = RankingEngine.rank_plans(plans, crop_clean, soil_ph, weather_summary)
            primary_rec = ranked_plans[0]

        # Process cost and schedule for the primary recommendation
        cost_summary = CostCalculator.calculate_solution_cost(primary_rec['items'], farm_area_acres=farm_area_val)
        primary_rec['items'] = cost_summary['items'] # Replace with detailed cost items
        
        schedule = ScheduleGenerator.generate_schedule(
            primary_rec['items'],
            crop=crop_clean
        )

        # STEP 8: Rule Engine
        agronomic_rules = AgronomicRuleEngine.evaluate_rules(
            deficiency_n=deficiency['N'],
            deficiency_p=deficiency['P'],
            deficiency_k=deficiency['K'],
            soil_ph=soil_ph,
            soil_type=soil_type_clean
        )

        # STEP 9: Explanation Generator
        explanation = ExplanationGenerator.generate_explanation(
            mode=mode,
            crop=crop_clean,
            soil_type=soil_type_clean,
            previous_crop=prev_crop_clean,
            ideal_npk=ideal_req,
            soil_npk=actual_soil,
            net_deficiency=deficiency,
            selected_solution=primary_rec,
            cost_summary=cost_summary,
            weather_summary=weather_summary,
            prev_crop_summary={'explanation': ''}
        )

        # Return full payload
        return {
            'mode': mode,
            'primary_recommendation': {
                'title': primary_rec['title'],
                'description': primary_rec['description'],
                'tag': primary_rec['tag'],
                'score': primary_rec.get('score', 100.0),
                'items': primary_rec['items'],
                'total_cost_inr': cost_summary.get('total_cost_inr', 0.0),
                'cost_per_acre_inr': cost_summary.get('cost_per_acre_inr', 0.0),
                'farm_area_acres': cost_summary.get('farm_area_acres', farm_area_val)
            },
            'alternative_options': [
                {
                    'title': p['title'],
                    'description': p['description'],
                    'tag': p['tag'],
                    'score': p.get('score', 0.0)
                } for p in ranked_plans[1:3]
            ],
            'application_schedule': schedule,
            'agronomic_advice': agronomic_rules,
            'ai_explanation': explanation
        }
