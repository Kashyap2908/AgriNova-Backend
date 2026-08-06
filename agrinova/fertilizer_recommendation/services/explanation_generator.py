"""
AI Explanation Generator Engine
Generates human-readable, professional agronomic AI explanations for fertilizer recommendations.
"""

import logging

logger = logging.getLogger(__name__)


class ExplanationGenerator:
    """
    Generates rich, transparent AI explanations detailing the agronomic reasoning behind the recommendation.
    """

    @staticmethod
    def generate_explanation(mode: str, crop: str, soil_type: str, previous_crop: str,
                             ideal_npk: dict, soil_npk: dict, net_deficiency: dict,
                             selected_solution: dict, cost_summary: dict,
                             weather_summary: dict, prev_crop_summary: dict) -> dict:

        mode_badge = "🎯 Precision Mode (Soil Health Card Active)" if mode == 'PRECISION' else "⚡ Smart Recommendation Mode (Agronometric Estimator)"

        # 1. Selection Overview
        overview = f"Selected {selected_solution['title']} for {crop.title()} on {cost_summary['farm_area_acres']} acre(s) of {soil_type.title()} soil."

        # 2. Nutrient Gap Reasoning
        gap_reasoning = (
            f"The total nutrient requirement for {crop.title()} is N: {ideal_npk['N']} kg/ha, P: {ideal_npk['P']} kg/ha, K: {ideal_npk['K']} kg/ha. "
            f"After analyzing soil test values (N: {soil_npk['N']}, P: {soil_npk['P']}, K: {soil_npk['K']} kg/ha), "
            f"the net field nutrient deficiency was determined as N: {net_deficiency['N']} kg/ha, P: {net_deficiency['P']} kg/ha, K: {net_deficiency['K']} kg/ha."
        )

        # 3. Previous Crop Credit Note
        prev_crop_note = prev_crop_summary.get('explanation', '')

        # 4. Combination Logic
        # 4. Combination Logic
        fert_names = [item['fertilizer_name'] for item in cost_summary['items']]
        
        # LP Dynamic specific text
        combo_logic = (f"The mathematical optimizer dynamically evaluated all fertilizers available in the master catalog. "
                       f"The selected combination ({selected_solution['title']}) provided the required nutrients "
                       f"while optimizing for {selected_solution['strategy']} goals. ")
        
        roles = []
        if any('Phosphatic' in item['type'] for item in cost_summary['items']):
            roles.append("Phosphatic fertilizers initiate root development")
        if any('Potassic' in item['type'] for item in cost_summary['items']):
            roles.append("Potassic fertilizers supply Potassium for crop disease resistance and quality")
        if any('Nitrogenous' in item['type'] for item in cost_summary['items']):
            roles.append("Nitrogenous fertilizers fuel vegetative growth")
            
        if roles:
            combo_logic += ", ".join(roles) + ". "
        
        combo_logic += f"Total estimated investment is ₹{cost_summary['total_cost_inr']} (₹{cost_summary['cost_per_acre_inr']} per acre)."

        # 5. Expected Yield & Health Impact
        expected_yield_pct = "15 - 25%" if mode == 'PRECISION' else "10 - 20%"

        return {
            'mode_badge': mode_badge,
            'overview': overview,
            'nutrient_gap_analysis': gap_reasoning,
            'previous_crop_impact': prev_crop_note,
            'fertilizer_matching_logic': combo_logic,
            'expected_yield_improvement': expected_yield_pct,
            'weather_advice': weather_summary.get('weather_advice', [])
        }
