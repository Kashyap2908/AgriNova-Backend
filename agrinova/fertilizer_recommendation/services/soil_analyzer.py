"""
Soil Analyzer — Estimates soil nutrient status, classifies nutrient levels, and calculates deficiencies.
Uses farmer input / Soil Health Card data when available, otherwise estimates dynamically from soil type, state, and crop history.
Tracks exact source per nutrient and NEVER stores estimated values into database.
"""

import logging

logger = logging.getLogger(__name__)

# Regional Indian Soil Baselines (Available N in kg/ha, P₂O₅ in kg/ha, K₂O in kg/ha, S in kg/ha, Zn in ppm, B in ppm, Ca in kg/ha, Mg in kg/ha, OC in %, pH)
SOIL_TYPE_BASELINES = {
    'black': {
        'N': 160.0, 'P': 18.0, 'K': 280.0, 'S': 12.0, 'Ca': 650.0, 'Mg': 250.0,
        'Zn': 0.8, 'B': 0.5, 'Fe': 5.5, 'Mn': 3.5, 'Cu': 0.6,
        'OC': 0.55, 'EC': 0.45, 'pH': 7.8, 'desc': 'Black Cotton Soil (Vertisol)'
    },
    'red': {
        'N': 130.0, 'P': 12.0, 'K': 150.0, 'S': 10.0, 'Ca': 350.0, 'Mg': 120.0,
        'Zn': 0.6, 'B': 0.4, 'Fe': 7.2, 'Mn': 4.0, 'Cu': 0.4,
        'OC': 0.40, 'EC': 0.25, 'pH': 6.2, 'desc': 'Red Soil (Alfisol)'
    },
    'alluvial': {
        'N': 210.0, 'P': 22.0, 'K': 220.0, 'S': 15.0, 'Ca': 500.0, 'Mg': 180.0,
        'Zn': 1.2, 'B': 0.6, 'Fe': 8.0, 'Mn': 4.5, 'Cu': 0.7,
        'OC': 0.65, 'EC': 0.35, 'pH': 7.2, 'desc': 'Alluvial Soil (Indo-Gangetic)'
    },
    'sandy': {
        'N': 100.0, 'P': 10.0, 'K': 110.0, 'S': 8.0, 'Ca': 250.0, 'Mg': 90.0,
        'Zn': 0.5, 'B': 0.3, 'Fe': 3.5, 'Mn': 2.0, 'Cu': 0.3,
        'OC': 0.30, 'EC': 0.20, 'pH': 7.5, 'desc': 'Sandy Arid Soil'
    },
    'loamy': {
        'N': 180.0, 'P': 20.0, 'K': 200.0, 'S': 14.0, 'Ca': 480.0, 'Mg': 160.0,
        'Zn': 1.0, 'B': 0.5, 'Fe': 6.5, 'Mn': 3.8, 'Cu': 0.5,
        'OC': 0.60, 'EC': 0.30, 'pH': 7.0, 'desc': 'Loamy Agricultural Soil'
    },
    'clay': {
        'N': 170.0, 'P': 16.0, 'K': 250.0, 'S': 12.0, 'Ca': 600.0, 'Mg': 220.0,
        'Zn': 0.9, 'B': 0.5, 'Fe': 6.0, 'Mn': 3.2, 'Cu': 0.5,
        'OC': 0.58, 'EC': 0.40, 'pH': 7.6, 'desc': 'Heavy Clay Soil'
    },
    'laterite': {
        'N': 110.0, 'P': 8.0, 'K': 120.0, 'S': 6.0, 'Ca': 200.0, 'Mg': 80.0,
        'Zn': 0.5, 'B': 0.3, 'Fe': 12.0, 'Mn': 5.0, 'Cu': 0.4,
        'OC': 0.45, 'EC': 0.18, 'pH': 5.5, 'desc': 'Acidic Laterite Soil'
    },
}

DEFAULT_BASELINE = {
    'N': 150.0, 'P': 15.0, 'K': 180.0, 'S': 10.0, 'Ca': 400.0, 'Mg': 150.0,
    'Zn': 0.8, 'B': 0.4, 'Fe': 6.0, 'Mn': 3.5, 'Cu': 0.5,
    'OC': 0.50, 'EC': 0.30, 'pH': 7.0, 'desc': 'Standard Agricultural Baseline'
}

LEGUME_CROPS = [
    'chickpea', 'gram', 'chana', 'pigeonpea', 'arhar', 'tur', 'moong', 'mung', 'urad',
    'black gram', 'green gram', 'soybean', 'soya', 'groundnut', 'peanut', 'pea', 'peas',
    'cowpea', 'lobia', 'lentil', 'masoor', 'clover', 'dhaincha', 'sunhemp', 'lucerne',
    'cluster bean', 'guar', 'pulses'
]

HEAVY_FEEDERS = [
    'sugarcane', 'cotton', 'maize', 'corn', 'paddy', 'rice', 'tobacco', 'potato', 'banana'
]


def classify_nutrient(nutrient_key: str, value: float) -> str:
    """
    Classify nutrient value into Indian standard categories:
    Very Low, Low, Medium, High, Very High.
    """
    val = float(value or 0.0)
    key = nutrient_key.upper()

    if key == 'N':  # kg/ha
        if val < 140: return 'Very Low'
        elif val < 280: return 'Low'
        elif val < 450: return 'Medium'
        elif val < 600: return 'High'
        else: return 'Very High'

    elif key in ('P', 'P2O5'):  # kg/ha
        if val < 10: return 'Very Low'
        elif val < 23: return 'Low'
        elif val < 56: return 'Medium'
        elif val < 80: return 'High'
        else: return 'Very High'

    elif key in ('K', 'K2O'):  # kg/ha
        if val < 110: return 'Very Low'
        elif val < 280: return 'Low'
        elif val < 400: return 'Medium'
        elif val < 550: return 'High'
        else: return 'Very High'

    elif key == 'S':  # kg/ha
        if val < 10: return 'Very Low'
        elif val < 15: return 'Low'
        elif val < 30: return 'Medium'
        elif val < 45: return 'High'
        else: return 'Very High'

    elif key == 'ZN':  # ppm
        if val < 0.6: return 'Very Low'
        elif val < 1.2: return 'Low'
        elif val < 2.5: return 'Medium'
        elif val < 4.0: return 'High'
        else: return 'Very High'

    elif key == 'B':  # ppm
        if val < 0.5: return 'Very Low'
        elif val < 0.7: return 'Low'
        elif val < 1.5: return 'Medium'
        elif val < 2.5: return 'High'
        else: return 'Very High'

    elif key == 'FE':  # ppm
        if val < 4.5: return 'Low'
        elif val < 10.0: return 'Medium'
        else: return 'High'

    elif key == 'MN':  # ppm
        if val < 2.0: return 'Low'
        elif val < 5.0: return 'Medium'
        else: return 'High'

    elif key == 'CU':  # ppm
        if val < 0.2: return 'Low'
        elif val < 0.8: return 'Medium'
        else: return 'High'

    elif key in ('OC', 'ORGANIC_CARBON'):  # %
        if val < 0.50: return 'Very Low'
        elif val < 0.75: return 'Low'
        elif val < 1.00: return 'Medium'
        elif val < 1.50: return 'High'
        else: return 'Very High'

    elif key in ('EC', 'ELECTRICAL_CONDUCTIVITY'):  # dS/m
        if val < 1.0: return 'Normal / Safe'
        elif val < 2.0: return 'Slightly Saline'
        elif val < 4.0: return 'Moderately Saline'
        else: return 'Highly Saline'

    elif key == 'PH':
        if val < 5.5: return 'Strongly Acidic'
        elif val < 6.5: return 'Slightly Acidic'
        elif val <= 7.5: return 'Neutral / Optimal'
        elif val <= 8.5: return 'Slightly Alkaline'
        else: return 'Strongly Alkaline'

    elif key == 'CA':  # kg/ha
        if val < 300: return 'Low'
        elif val < 800: return 'Medium'
        else: return 'High'

    elif key == 'MG':  # kg/ha
        if val < 100: return 'Low'
        elif val < 300: return 'Medium'
        else: return 'High'

    return 'Medium'


def estimate_soil_nutrients(soil_type: str = '', state: str = '', season: str = '',
                             previous_crop: str = '') -> dict:
    """
    Estimate baseline soil parameters from soil type, state, and previous cropping history.
    """
    soil_key = (soil_type or '').strip().lower()

    matched = None
    for key, data in SOIL_TYPE_BASELINES.items():
        if key in soil_key:
            matched = data.copy()
            break
    if not matched:
        matched = DEFAULT_BASELINE.copy()

    n_val = matched['N']
    p_val = matched['P']
    k_val = matched['K']
    s_val = matched['S']
    ca_val = matched['Ca']
    mg_val = matched['Mg']
    zn_val = matched['Zn']
    b_val = matched['B']
    fe_val = matched['Fe']
    mn_val = matched['Mn']
    cu_val = matched['Cu']
    oc_val = matched['OC']
    ec_val = matched['EC']
    ph_val = matched['pH']

    # State adjustments
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
    elif any(s in state_key for s in ['rajasthan']):
        ph_val = min(8.3, ph_val + 0.3)

    # Previous crop adjustments
    prev_clean = (previous_crop or '').strip().lower()
    prev_note = ''
    if prev_clean and prev_clean not in ['none', 'fallow', 'n/a', 'select', '']:
        if any(leg in prev_clean for leg in LEGUME_CROPS):
            n_val += 25.0
            p_val += 5.0
            prev_note = f"Legume N-Credit: Previous crop ({previous_crop}) added ~25 kg/ha Nitrogen through biological fixation."
        elif any(hf in prev_clean for hf in HEAVY_FEEDERS):
            n_val -= 15.0
            p_val -= 5.0
            k_val -= 10.0
            prev_note = f"Depletion Adjusted: Previous crop ({previous_crop}) was a heavy feeder, reducing residual soil nutrients."

    source_label = f"Estimated from {matched['desc']}"

    return {
        'N': round(max(0, n_val), 1),
        'P': round(max(0, p_val), 1),
        'K': round(max(0, k_val), 1),
        'S': round(max(0, s_val), 1),
        'Ca': round(max(0, ca_val), 1),
        'Mg': round(max(0, mg_val), 1),
        'Zn': round(max(0, zn_val), 2),
        'B': round(max(0, b_val), 2),
        'Fe': round(max(0, fe_val), 2),
        'Mn': round(max(0, mn_val), 2),
        'Cu': round(max(0, cu_val), 2),
        'OC': round(max(0, oc_val), 2),
        'EC': round(max(0, ec_val), 2),
        'pH': round(ph_val, 1),
        'is_estimated': True,
        'source': source_label,
        'previous_crop_note': prev_note,
    }


def calculate_deficiency(ideal: dict, actual: dict) -> dict:
    """
    Calculate nutrient deficiency: ideal requirement - available soil nutrients.
    Returns dict with deficiency values (0 if surplus) and status labels.
    """
    def _def(key):
        i = float(ideal.get(key, 0))
        a = float(actual.get(key, 0))
        deficit = max(0.0, i - a)
        surplus = max(0.0, a - i)
        if deficit > 5:
            status = 'Deficient'
        elif surplus > 15:
            status = 'Excess'
        else:
            status = 'Adequate'
        return {
            'ideal': round(i, 1),
            'available': round(a, 1),
            'deficit': round(deficit, 1),
            'surplus': round(surplus, 1),
            'recommended_supply': round(deficit, 1),
            'status': status,
        }

    return {
        'N': _def('N'),
        'P': _def('P'),
        'K': _def('K'),
        'S': _def('S'),
        'Zn': _def('Zn'),
        'B': _def('B'),
    }


def get_soil_summary(nitrogen=None, phosphorus=None, potassium=None, soil_ph=None,
                      sulphur=None, calcium=None, magnesium=None,
                      zinc=None, boron=None, iron=None, manganese=None, copper=None,
                      organic_carbon=None, electrical_conductivity=None, soil_moisture=None,
                      soil_type='', state='', season='', previous_crop='') -> dict:
    """
    Build complete soil analysis summary with nutrient classification, source tracking per nutrient,
    and deficiency calculations. Accepts both farmer inputs and estimated fallbacks.
    """
    soil_type_clean = (soil_type or 'Loamy').strip()
    est_baseline = estimate_soil_nutrients(soil_type_clean, state, season, previous_crop)
    default_source = est_baseline['source']

    # Helper function to extract user value or fallback to estimate, and set individual source tag
    def _resolve(val, est_val):
        if val is not None and str(val).strip() != '' and float(val or 0) >= 0:
            return float(val), "Farmer Input"
        return float(est_val), default_source

    n_val, n_src = _resolve(nitrogen, est_baseline['N'])
    p_val, p_src = _resolve(phosphorus, est_baseline['P'])
    k_val, k_src = _resolve(potassium, est_baseline['K'])
    s_val, s_src = _resolve(sulphur, est_baseline['S'])
    ca_val, ca_src = _resolve(calcium, est_baseline['Ca'])
    mg_val, mg_src = _resolve(magnesium, est_baseline['Mg'])

    zn_val, zn_src = _resolve(zinc, est_baseline['Zn'])
    b_val, b_src = _resolve(boron, est_baseline['B'])
    fe_val, fe_src = _resolve(iron, est_baseline['Fe'])
    mn_val, mn_src = _resolve(manganese, est_baseline['Mn'])
    cu_val, cu_src = _resolve(copper, est_baseline['Cu'])

    oc_val, oc_src = _resolve(organic_carbon, est_baseline['OC'])
    ec_val, ec_src = _resolve(electrical_conductivity, est_baseline['EC'])
    ph_val, ph_src = _resolve(soil_ph, est_baseline['pH'])
    moist_val = float(soil_moisture) if soil_moisture is not None and str(soil_moisture).strip() != '' else None

    # Track overall soil card status
    has_farmer_input = any(
        src == "Farmer Input" for src in [n_src, p_src, k_src, s_src, zn_src, b_src, oc_src, ph_src]
    )
    mode = 'PRECISION' if has_farmer_input else 'ESTIMATED'

    soil_nutrients = {
        'N': n_val, 'P': p_val, 'K': k_val, 'S': s_val, 'Ca': ca_val, 'Mg': mg_val,
        'Zn': zn_val, 'B': b_val, 'Fe': fe_val, 'Mn': mn_val, 'Cu': cu_val,
        'OC': oc_val, 'EC': ec_val, 'pH': ph_val, 'soil_moisture': moist_val,
        'is_estimated': not has_farmer_input,
        'source': 'Farmer Soil Health Card' if has_farmer_input else default_source,
        'previous_crop_note': est_baseline.get('previous_crop_note', '')
    }

    # Nutrient individual metadata mapping
    sources_map = {
        'N': n_src, 'P': p_src, 'K': k_src, 'S': s_src, 'Ca': ca_src, 'Mg': mg_src,
        'Zn': zn_src, 'B': b_src, 'Fe': fe_src, 'Mn': mn_src, 'Cu': cu_src,
        'OC': oc_src, 'EC': ec_src, 'pH': ph_src
    }

    classifications_map = {
        'N': classify_nutrient('N', n_val),
        'P': classify_nutrient('P', p_val),
        'K': classify_nutrient('K', k_val),
        'S': classify_nutrient('S', s_val),
        'Ca': classify_nutrient('Ca', ca_val),
        'Mg': classify_nutrient('Mg', mg_val),
        'Zn': classify_nutrient('Zn', zn_val),
        'B': classify_nutrient('B', b_val),
        'Fe': classify_nutrient('Fe', fe_val),
        'Mn': classify_nutrient('Mn', mn_val),
        'Cu': classify_nutrient('Cu', cu_val),
        'OC': classify_nutrient('OC', oc_val),
        'EC': classify_nutrient('EC', ec_val),
        'pH': classify_nutrient('pH', ph_val),
    }

    return {
        'mode': mode,
        'soil_nutrients': soil_nutrients,
        'nutrient_sources': sources_map,
        'nutrient_classifications': classifications_map,
        'soil_type': soil_type_clean,
        'has_soil_card': has_farmer_input,
    }

