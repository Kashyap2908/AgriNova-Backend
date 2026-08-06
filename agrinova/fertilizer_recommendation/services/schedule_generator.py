"""
Split Application Schedule Generator Engine
Generates stage-wise split application timelines (Basal, Vegetative, Flowering/Grain filling) tailored to crop type.
Dynamically schedules any fertilizer based on fertilizer type ('Nitrogenous', 'Phosphatic', 'Potassic').
"""

import logging

logger = logging.getLogger(__name__)

CROP_STAGE_MAP = {
    'rice': [
        {'stage': 'Basal / Sowing', 'timing': 'At transplanting / sowing', 'pct_n': 50, 'pct_p': 100, 'pct_k': 50, 'advice': 'Apply full Phosphatic dose + 50% Nitrogen + 50% Potassic fertilizer basal incorporation.'},
        {'stage': 'Active Tillering', 'timing': '20-25 days after transplanting (DAT)', 'pct_n': 25, 'pct_p': 0, 'pct_k': 0, 'advice': 'Top-dress 25% Nitrogen with standing water level 2-3 cm.'},
        {'stage': 'Panicle Initiation', 'timing': '40-45 days after transplanting (DAT)', 'pct_n': 25, 'pct_p': 0, 'pct_k': 50, 'advice': 'Top-dress remaining 25% Nitrogen + 50% Potassium for robust grain filling.'}
    ],
    'paddy': [
        {'stage': 'Basal / Sowing', 'timing': 'At transplanting / sowing', 'pct_n': 50, 'pct_p': 100, 'pct_k': 50, 'advice': 'Apply full Phosphatic dose + 50% Nitrogen + 50% Potassic fertilizer.'},
        {'stage': 'Active Tillering', 'timing': '20-25 days after transplanting', 'pct_n': 25, 'pct_p': 0, 'pct_k': 0, 'advice': 'Top-dress 25% Nitrogen.'},
        {'stage': 'Panicle Initiation', 'timing': '40-45 days after transplanting', 'pct_n': 25, 'pct_p': 0, 'pct_k': 50, 'advice': 'Top-dress remaining 25% Nitrogen + 50% Potassium.'}
    ],
    'wheat': [
        {'stage': 'Basal / Sowing', 'timing': 'At sowing time', 'pct_n': 50, 'pct_p': 100, 'pct_k': 100, 'advice': 'Incorporate full P & K + 50% Nitrogen at 5 cm depth before sowing.'},
        {'stage': 'CRI (Crown Root Initiation)', 'timing': '21-25 days after sowing (DAS)', 'pct_n': 25, 'pct_p': 0, 'pct_k': 0, 'advice': 'Broadcast 25% Nitrogen immediately before 1st irrigation.'},
        {'stage': 'Booting / Jointing Stage', 'timing': '40-45 days after sowing (DAS)', 'pct_n': 25, 'pct_p': 0, 'pct_k': 0, 'advice': 'Top-dress final 25% Nitrogen before 2nd irrigation.'}
    ],
    'maize': [
        {'stage': 'Basal / Sowing', 'timing': 'At planting', 'pct_n': 33, 'pct_p': 100, 'pct_k': 100, 'advice': 'Apply full P & K + 33% Nitrogen.'},
        {'stage': 'Knee High Stage', 'timing': '30-35 days after planting', 'pct_n': 33, 'pct_p': 0, 'pct_k': 0, 'advice': 'Side-dress 33% Nitrogen near root zone.'},
        {'stage': 'Tasseling / Silking', 'timing': '55-60 days after planting', 'pct_n': 34, 'pct_p': 0, 'pct_k': 0, 'advice': 'Apply final 34% Nitrogen dose.'}
    ],
    'cotton': [
        {'stage': 'Basal / Sowing', 'timing': 'At sowing', 'pct_n': 25, 'pct_p': 100, 'pct_k': 50, 'advice': 'Apply full P + 50% K + 25% N.'},
        {'stage': 'Square Formation', 'timing': '40-45 DAS', 'pct_n': 50, 'pct_p': 0, 'pct_k': 0, 'advice': 'Side-dress 50% N.'},
        {'stage': 'Peak Flowering / Boll Development', 'timing': '70-75 DAS', 'pct_n': 25, 'pct_p': 0, 'pct_k': 50, 'advice': 'Apply remaining 25% N + 50% K.'}
    ]
}

DEFAULT_STAGES = [
    {'stage': 'Basal / Sowing', 'timing': 'At planting / sowing', 'pct_n': 50, 'pct_p': 100, 'pct_k': 50, 'advice': 'Incorporate full P & 50% K + 50% N during basal field prep.'},
    {'stage': 'Vegetative / Active Growth', 'timing': '30 days after sowing', 'pct_n': 25, 'pct_p': 0, 'pct_k': 0, 'advice': 'Top-dress 25% Nitrogen.'},
    {'stage': 'Flowering & Grain Filling', 'timing': '60 days after sowing', 'pct_n': 25, 'pct_p': 0, 'pct_k': 50, 'advice': 'Apply final 25% N + 50% K for optimal yield development.'}
]


class ScheduleGenerator:
    """
    Generates tailored stage-wise split application schedule dynamically based on fertilizer types.
    """

    @staticmethod
    def generate_schedule(arg1, arg2=None, crop: str = '', items: list = None) -> list:
        """
        Dynamically schedules any fertilizer based on its type.
        - If fert['type'] contains 'Nitrogenous': split between basal and top-dressing (e.g. 50/50).
        - If fert['type'] contains 'Phosphatic' or 'Potassic': 100% in Basal.
        No hardcoded fertilizer string matches.
        """
        if isinstance(arg1, list):
            items_list = arg1
            crop_clean = (arg2 or crop or '').strip().lower()
        elif isinstance(arg2, list):
            items_list = arg2
            crop_clean = (arg1 or crop or '').strip().lower()
        else:
            items_list = items or []
            crop_clean = (crop or '').strip().lower()

        matched_stages = DEFAULT_STAGES
        for c_key, stages in CROP_STAGE_MAP.items():
            if c_key in crop_clean or crop_clean in c_key:
                matched_stages = stages
                break

        schedule = []

        for stage_idx, stage in enumerate(matched_stages):
            stage_items = []
            for item in items_list:
                if not isinstance(item, dict):
                    continue

                fert = item.get('fertilizer', {}) if isinstance(item, dict) and 'fertilizer' in item else item
                fert_name = fert.get('name') or item.get('fertilizer_name') or 'Fertilizer'
                fert_type = str(fert.get('type') or item.get('type') or '').strip().lower()

                dose_per_acre = float(item.get('dose_per_acre_kg', 0.0) or 0.0)
                total_qty = float(item.get('total_quantity_kg', 0.0) or 0.0)
                if dose_per_acre == 0.0 and 'dose_kg_ha' in item:
                    dose_per_acre = round(float(item['dose_kg_ha']) / 2.47105, 1)

                # Dynamic type checking:
                is_nitrogenous = 'nitrogenous' in fert_type
                is_phosphatic_or_potassic = 'phosphatic' in fert_type or 'potassic' in fert_type

                if is_phosphatic_or_potassic:
                    # Put 100% in Basal (stage_idx == 0)
                    pct = 100.0 if stage_idx == 0 else 0.0
                elif is_nitrogenous:
                    # Split between basal and top-dressing (e.g. 50% basal, 25% stage 2, 25% stage 3)
                    pct = float(stage.get('pct_n', 50.0))
                else:
                    # Fallback for unclassified types
                    if 'phosph' in fert_type or 'potass' in fert_type or 'potash' in fert_type:
                        pct = 100.0 if stage_idx == 0 else 0.0
                    else:
                        pct = float(stage.get('pct_n', 50.0))

                stage_qty_per_acre = round(dose_per_acre * (pct / 100.0), 1)
                stage_total_qty = round(total_qty * (pct / 100.0), 1)

                if pct > 0:
                    stage_items.append({
                        'fertilizer_name': fert_name,
                        'stage_dose_per_acre_kg': stage_qty_per_acre,
                        'stage_total_kg': stage_total_qty,
                        'split_percentage': pct
                    })

            schedule.append({
                'stage_name': stage['stage'],
                'recommended_timing': stage['timing'],
                'application_instructions': stage['advice'],
                'fertilizer_split': stage_items
            })

        return schedule


def generate_schedule(arg1, arg2=None, crop: str = '', items: list = None) -> list:
    return ScheduleGenerator.generate_schedule(arg1, arg2=arg2, crop=crop, items=items)

