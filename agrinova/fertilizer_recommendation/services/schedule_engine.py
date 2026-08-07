"""
Schedule Engine — Dataset-driven stage-wise split schedule generator.
Reads split application percentages and instructions from crop_growth_stage_schedule.csv via data_loader.
Builds visual application timeline data for frontend & downloadable PDF schedule.
"""

import logging
from .data_loader import load_growth_stage_schedule
from .area_converter import to_hectares, format_quantity

logger = logging.getLogger(__name__)


def generate_split_schedule(crop: str, plan_items: list, farm_area: float, area_unit: str) -> list:
    """
    Generate stage-wise split application schedule for a fertilizer plan.
    plan_items: list of {'fertilizer': dict, 'dose_kg_ha': float}
    Returns list of stage dicts containing nutrient splits, fertilizer dosages, and application instructions.
    """
    schedules_db = load_growth_stage_schedule()
    crop_clean = (crop or '').strip().lower()

    # Find matching schedule
    stage_rules = schedules_db.get(crop_clean)

    if not stage_rules:
        # Partial match
        for c_key, rules in schedules_db.items():
            if c_key in crop_clean or crop_clean in c_key:
                stage_rules = rules
                break

    if not stage_rules:
        stage_rules = schedules_db.get('default', [
            {
                'stage': 'Basal / Sowing',
                'stage_order': 1,
                'days_after_sowing': 0,
                'N_split_pct': 50.0,
                'P_split_pct': 100.0,
                'K_split_pct': 50.0,
                'application_method': 'Soil Incorporation',
                'instructions': 'Apply full P₂O₅ + 50% N + 50% K₂O as basal incorporation during land preparation.',
            },
            {
                'stage': 'Vegetative Growth',
                'stage_order': 2,
                'days_after_sowing': 30,
                'N_split_pct': 25.0,
                'P_split_pct': 0.0,
                'K_split_pct': 0.0,
                'application_method': 'Top Dressing',
                'instructions': 'Top-dress 25% Nitrogen during active growth phase.',
            },
            {
                'stage': 'Flowering / Grain Filling',
                'stage_order': 3,
                'days_after_sowing': 60,
                'N_split_pct': 25.0,
                'P_split_pct': 0.0,
                'K_split_pct': 50.0,
                'application_method': 'Top Dressing',
                'instructions': 'Apply remaining 25% N + 50% K₂O for reproductive development.',
            },
        ])

    area_ha = to_hectares(farm_area, area_unit)

    schedule_output = []

    for rule in stage_rules:
        stage_name = rule['stage']
        days = rule['days_after_sowing']
        n_pct = rule['N_split_pct']
        p_pct = rule['P_split_pct']
        k_pct = rule['K_split_pct']
        method = rule['application_method']
        instructions = rule['instructions']

        stage_fertilizers = []

        for item in plan_items:
            fert = item['fertilizer']
            total_dose_ha = item['dose_kg_ha']

            # Determine split fraction for this fertilizer based on its primary nutrient
            fn = fert.get('N_pct', 0.0)
            fp = fert.get('P_pct', 0.0)
            fk = fert.get('K_pct', 0.0)

            # Assign split ratio
            if fp > 20 and fn <= 20:  # Phosphatic dominant (DAP, SSP, MAP)
                split_frac = p_pct / 100.0
            elif fk > 30 and fn <= 15:  # Potassic dominant (MOP, SOP)
                split_frac = k_pct / 100.0
            elif fn > 30 and fp <= 5 and fk <= 5:  # Nitrogenous dominant (Urea)
                split_frac = n_pct / 100.0
            else:  # Complex / NPK balanced
                denom = max(1.0, fn + fp + fk)
                split_frac = ((fn * n_pct) + (fp * p_pct) + (fk * k_pct)) / (100.0 * denom)

            if split_frac <= 0.01:
                continue

            stage_dose_ha = round(total_dose_ha * split_frac, 1)
            stage_total_kg = round(stage_dose_ha * area_ha, 1)

            if stage_total_kg <= 0.1:
                continue

            qty_display = format_quantity(stage_total_kg, farm_area, area_unit)

            stage_fertilizers.append({
                'name': fert['name'],
                'type': fert['type'],
                'dose_per_ha': stage_dose_ha,
                'total_kg': stage_total_kg,
                'quantity_display': qty_display,
                'unit': fert.get('unit', 'kg'),
                'application_method': method,
            })

        schedule_output.append({
            'stage': stage_name,
            'stage_order': rule['stage_order'],
            'timing': 'Day 0 (At Sowing / Transplanting)' if days == 0 else f"Day {days} ({days} Days After Sowing)",
            'days_after_sowing': days,
            'nutrient_splits': {
                'N_split_pct': n_pct,
                'P_split_pct': p_pct,
                'K_split_pct': k_pct,
            },
            'application_method': method,
            'instructions': instructions,
            'fertilizers': stage_fertilizers,
            'weather_note': 'Ensure sufficient soil moisture before application. Avoid broadcasting under strong wind or imminent heavy rain.'
        })

    return schedule_output
