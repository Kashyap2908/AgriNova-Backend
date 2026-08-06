"""
Soil Nutrient & Regional Efficiency Estimation Engine
Estimates available soil NPK, pH, and nutrient uptake efficiency factors based on Soil Type, State, and Season.
"""

import logging

logger = logging.getLogger(__name__)

# Regional Indian Soil & Climate Baselines
SOIL_TYPE_BASELINES = {
    'black': {
        'N': 160.0, 'P': 18.0, 'K': 280.0, 'pH': 7.8,
        'eff_n': 1.02, 'eff_p': 1.10, 'eff_k': 0.85,  # Vertisol holds K well, fixes P slightly
        'desc': 'Black Soil (Vertisol) - High clay, potassium rich'
    },
    'red': {
        'N': 130.0, 'P': 12.0, 'K': 150.0, 'pH': 6.2,
        'eff_n': 1.08, 'eff_p': 1.22, 'eff_k': 1.10,  # Acidic P fixation requires higher P dose
        'desc': 'Red Soil (Alfisol) - Low P availability, acidic tendency'
    },
    'alluvial': {
        'N': 210.0, 'P': 22.0, 'K': 220.0, 'pH': 7.2,
        'eff_n': 1.00, 'eff_p': 1.00, 'eff_k': 1.00,  # Highly fertile Indo-Gangetic plains
        'desc': 'Alluvial Soil - Fertile plain soil, balanced nutrient availability'
    },
    'sandy': {
        'N': 100.0, 'P': 10.0, 'K': 110.0, 'pH': 7.5,
        'eff_n': 1.25, 'eff_p': 1.15, 'eff_k': 1.20,  # High leaching losses require 20-25% higher dose
        'desc': 'Sandy Soil - High leaching rate, low nutrient retention'
    },
    'loamy': {
        'N': 180.0, 'P': 20.0, 'K': 200.0, 'pH': 7.0,
        'eff_n': 1.00, 'eff_p': 1.00, 'eff_k': 1.00,  # Ideal agricultural loam
        'desc': 'Loamy Soil - Well-balanced nutrient retention and aeration'
    },
    'clay': {
        'N': 170.0, 'P': 16.0, 'K': 250.0, 'pH': 7.6,
        'eff_n': 0.98, 'eff_p': 1.12, 'eff_k': 0.90,  # High clay holds moisture & K
        'desc': 'Clay Heavy Soil - High moisture & potassium retention'
    },
    'laterite': {
        'N': 110.0, 'P': 8.0, 'K': 120.0, 'pH': 5.5,
        'eff_n': 1.15, 'eff_p': 1.30, 'eff_k': 1.15,  # Strongly acidic, high Fe/Al P-fixation
        'desc': 'Laterite Soil - Acidic, high phosphorus fixation capacity'
    },
}

DEFAULT_BASELINE = {
    'N': 150.0, 'P': 15.0, 'K': 180.0, 'pH': 7.0,
    'eff_n': 1.00, 'eff_p': 1.00, 'eff_k': 1.00,
    'desc': 'Standard Agricultural Baseline'
}


class SoilNutrientEstimator:
    """
    Estimates baseline soil NPK, pH, and regional agronomic efficiency multipliers.
    """

    @staticmethod
    def estimate_soil_nutrients(soil_type: str = '', state: str = '', season: str = '') -> dict:
        soil_key = (soil_type or '').strip().lower()

        # 1. Match Soil Baseline & Efficiency Multipliers
        matched_baseline = None
        for key, data in SOIL_TYPE_BASELINES.items():
            if key in soil_key:
                matched_baseline = data.copy()
                break

        if not matched_baseline:
            matched_baseline = DEFAULT_BASELINE.copy()

        # 2. State & Regional Agro-Climatic Adjustments
        state_key = (state or '').strip().lower()
        state_n_mod = 1.0
        state_p_mod = 1.0
        state_k_mod = 1.0

        if any(s in state_key for s in ['punjab', 'haryana', 'uttar pradesh']):
            matched_baseline['N'] += 25.0
            matched_baseline['P'] += 5.0
            state_n_mod = 1.05
        elif any(s in state_key for s in ['bihar', 'west bengal', 'assam', 'odisha']):
            matched_baseline['N'] -= 10.0  # Higher monsoon leaching
            matched_baseline['P'] -= 3.0
            state_n_mod = 1.12  # Higher N requirement due to leaching
        elif any(s in state_key for s in ['madhya pradesh', 'maharashtra', 'gujarat']):
            matched_baseline['K'] += 30.0  # Black soil region
            matched_baseline['pH'] = min(8.2, matched_baseline['pH'] + 0.3)
        elif any(s in state_key for s in ['karnataka', 'tamil nadu', 'kerala', 'andhra']):
            matched_baseline['K'] += 15.0
            matched_baseline['pH'] = max(5.8, matched_baseline['pH'] - 0.3)
            state_p_mod = 1.10
        elif any(s in state_key for s in ['rajasthan']):
            matched_baseline['pH'] = min(8.3, matched_baseline['pH'] + 0.4)
            state_n_mod = 1.08

        # 3. Season Adjustments (Monsoon Kharif vs Winter Rabi vs Summer Zaid)
        season_key = (season or '').strip().lower()
        season_n_mod = 1.0
        if 'kharif' in season_key:
            season_n_mod = 1.08  # Monsoon rainfall N leaching
        elif 'zaid' in season_key or 'summer' in season_key:
            season_n_mod = 1.12  # High heat volatilization loss

        final_eff_n = round(matched_baseline['eff_n'] * state_n_mod * season_n_mod, 3)
        final_eff_p = round(matched_baseline['eff_p'] * state_p_mod, 3)
        final_eff_k = round(matched_baseline['eff_k'] * state_k_mod, 3)

        return {
            'estimated_n': round(matched_baseline['N'], 1),
            'estimated_p': round(matched_baseline['P'], 1),
            'estimated_k': round(matched_baseline['K'], 1),
            'estimated_ph': round(matched_baseline['pH'], 1),
            'eff_n': final_eff_n,
            'eff_p': final_eff_p,
            'eff_k': final_eff_k,
            'baseline_source': matched_baseline['desc'],
            'is_estimated': True
        }
