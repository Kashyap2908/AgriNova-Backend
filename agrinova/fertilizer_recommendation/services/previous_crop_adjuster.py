"""
Previous Crop Adjustment Engine
Calculates nitrogen fixation credit from preceding legume crops and nutrient depletion adjustments from heavy feeders.
"""

import logging

logger = logging.getLogger(__name__)

LEGUME_CROPS = [
    'chickpea', 'gram', 'chana', 'pigeonpea', 'arhar', 'tur', 'moong', 'mung', 'urad',
    'black gram', 'green gram', 'soybean', 'soya', 'groundnut', 'peanut', 'pea', 'peas',
    'cowpea', 'lobia', 'lentil', 'masoor', 'clover', 'dhaincha', 'sunhemp', 'lucerne',
    'cluster bean', 'guar', 'pulses'
]

HEAVY_FEEDERS = [
    'sugarcane', 'cotton', 'maize', 'corn', 'paddy', 'rice', 'tobacco', 'potato', 'banana'
]


class PreviousCropAdjuster:
    """
    Calculates nutrient adjustment factors based on the previous crop grown on the farm plot.
    """

    @staticmethod
    def calculate_adjustment(previous_crop: str = '') -> dict:
        prev_clean = (previous_crop or '').strip().lower()

        if not prev_clean or prev_clean in ['none', 'fallow', 'n/a', 'select']:
            return {
                'n_adj_kg_ha': 0.0,
                'p_adj_kg_ha': 0.0,
                'k_adj_kg_ha': 0.0,
                'credit_type': 'NEUTRAL',
                'explanation': 'No previous crop credit applied.'
            }

        # Check if Legume (Biological Nitrogen Fixation Credit)
        is_legume = any(leg in prev_clean for leg in LEGUME_CROPS)
        if is_legume:
            # Legumes leave 20 to 30 kg/ha nitrogen credit in soil root zone
            n_credit = -25.0
            return {
                'n_adj_kg_ha': n_credit,
                'p_adj_kg_ha': -5.0,  # Legumes increase organic P availability
                'k_adj_kg_ha': 0.0,
                'credit_type': 'LEGUME_N_FIXATION_CREDIT',
                'explanation': f"Preceding crop ({previous_crop.title()}) is a Legume with root nodule rhizobia. Applied ~25 kg/ha Nitrogen credit deduction to save fertilizer costs."
            }

        # Check if Heavy Feeder (Nutrient Depletion Surcharge)
        is_heavy = any(hf in prev_clean for hf in HEAVY_FEEDERS)
        if is_heavy:
            return {
                'n_adj_kg_ha': 15.0,
                'p_adj_kg_ha': 5.0,
                'k_adj_kg_ha': 10.0,
                'credit_type': 'HEAVY_FEEDER_DEPLETION',
                'explanation': f"Preceding crop ({previous_crop.title()}) is a heavy soil nutrient feeder. Added slight nutrient supplement to replenish depleted soil reserves."
            }

        return {
            'n_adj_kg_ha': 0.0,
            'p_adj_kg_ha': 0.0,
            'k_adj_kg_ha': 0.0,
            'credit_type': 'STANDARD',
            'explanation': f"Preceding crop ({previous_crop.title()}) noted. Standard baseline requirement applied."
        }
