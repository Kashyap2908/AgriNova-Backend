import logging

logger = logging.getLogger(__name__)

SOIL_TYPE_BASELINES = {
    'black': {'N': 160.0, 'P': 18.0, 'K': 280.0},
    'red': {'N': 130.0, 'P': 12.0, 'K': 150.0},
    'alluvial': {'N': 210.0, 'P': 22.0, 'K': 220.0},
    'sandy': {'N': 100.0, 'P': 10.0, 'K': 110.0},
    'loamy': {'N': 180.0, 'P': 20.0, 'K': 200.0},
    'clay': {'N': 170.0, 'P': 16.0, 'K': 250.0},
    'laterite': {'N': 110.0, 'P': 8.0, 'K': 120.0},
}

DEFAULT_BASELINE = {'N': 150.0, 'P': 15.0, 'K': 180.0}

LEGUME_CROPS = [
    'chickpea', 'gram', 'chana', 'pigeonpea', 'arhar', 'tur', 'moong', 'mung', 'urad',
    'black gram', 'green gram', 'soybean', 'soya', 'groundnut', 'peanut', 'pea', 'peas',
    'cowpea', 'lobia', 'lentil', 'masoor', 'clover', 'dhaincha', 'sunhemp', 'lucerne',
    'cluster bean', 'guar', 'pulses'
]

HEAVY_FEEDERS = [
    'sugarcane', 'cotton', 'maize', 'corn', 'paddy', 'rice', 'tobacco', 'potato', 'banana'
]


class SoilEstimationEngine:
    """
    Engine to estimate soil available nutrients (N, P, K) based on Soil Type, State, Season, and Previous Crop.
    """

    @staticmethod
    def estimate_soil_nutrients(soil_type: str = '', state: str = '', season: str = '', prev_crop: str = '') -> dict:
        """
        Estimates soil N, P, K levels.
        Returns a clean dictionary: {'N': float, 'P': float, 'K': float}
        """
        soil_key = (soil_type or '').strip().lower()

        # 1. Match Soil Baseline
        matched_baseline = None
        for key, data in SOIL_TYPE_BASELINES.items():
            if key in soil_key:
                matched_baseline = data.copy()
                break

        if not matched_baseline:
            matched_baseline = DEFAULT_BASELINE.copy()

        n_val = matched_baseline['N']
        p_val = matched_baseline['P']
        k_val = matched_baseline['K']

        # 2. State & Regional Adjustments
        state_key = (state or '').strip().lower()
        if any(s in state_key for s in ['punjab', 'haryana', 'uttar pradesh']):
            n_val += 25.0
            p_val += 5.0
        elif any(s in state_key for s in ['bihar', 'west bengal', 'assam', 'odisha']):
            n_val -= 10.0
            p_val -= 3.0
        elif any(s in state_key for s in ['madhya pradesh', 'maharashtra', 'gujarat']):
            k_val += 30.0
        elif any(s in state_key for s in ['karnataka', 'tamil nadu', 'kerala', 'andhra']):
            k_val += 15.0

        # 3. Previous Crop Adjustments
        prev_clean = (prev_crop or '').strip().lower()
        if prev_clean and prev_clean not in ['none', 'fallow', 'n/a', 'select']:
            if any(leg in prev_clean for leg in LEGUME_CROPS):
                n_val += 25.0
                p_val += 5.0
            elif any(hf in prev_clean for hf in HEAVY_FEEDERS):
                n_val -= 15.0
                p_val -= 5.0
                k_val -= 10.0

        return {
            'N': float(round(n_val, 1)),
            'P': float(round(p_val, 1)),
            'K': float(round(k_val, 1))
        }
