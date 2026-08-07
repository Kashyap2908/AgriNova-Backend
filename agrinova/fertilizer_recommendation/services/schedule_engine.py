"""
Schedule Engine — Dataset-driven & agronomic stage-wise split schedule generator.
Reads split application percentages and instructions from crop_growth_stage_schedule.csv via data_loader.
Builds crop-specific application timelines with distinct growth stages and Days After Sowing (DAS).
"""

import logging
from .data_loader import load_growth_stage_schedule
from .area_converter import to_hectares, format_quantity

logger = logging.getLogger(__name__)

LEGUMES = ['groundnut', 'peanut', 'soybean', 'chickpea', 'gram', 'moong', 'urad', 'pigeonpea', 'arhar', 'tur', 'pea', 'lentil']
CEREALS = ['wheat', 'rice', 'paddy', 'maize', 'corn', 'jowar', 'sorghum', 'bajra', 'ragi']
COMMERCIAL = ['cotton', 'sugarcane', 'potato', 'onion', 'garlic', 'tomato', 'chilli', 'brinjal', 'banana', 'papaya', 'mango', 'turmeric', 'ginger']


def generate_split_schedule(crop: str, plan_items: list, farm_area: float, area_unit: str) -> list:
    """
    Generate stage-wise split application schedule for a fertilizer plan.
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
        stage_rules = _get_default_crop_family_schedule(crop_clean)

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

            fn = fert.get('N_pct', 0.0)
            fp = fert.get('P_pct', 0.0)
            fk = fert.get('K_pct', 0.0)
            ftype = fert.get('type', '').lower()
            fname = fert.get('name', '').lower()

            # Assign split ratio based on fertilizer function & stage
            if 'gypsum' in fname or 'rhizobium' in fname or 'bio' in ftype:
                # Soil amendments / biofertilizers applied at basal or pegging
                if days == 0 and ('basal' in stage_name.lower() or 'sowing' in stage_name.lower() or 'prep' in stage_name.lower()):
                    split_frac = 1.0 if 'gypsum' not in fname else 0.5
                elif days >= 35 and ('pegging' in stage_name.lower() or 'flowering' in stage_name.lower()):
                    split_frac = 0.5 if 'gypsum' in fname else 0.0
                else:
                    split_frac = 0.0
            elif 'water soluble' in ftype or '19-19-19' in fname or 'boron' in fname or 'edta' in fname:
                # Foliar sprays applied during vegetative or flowering/fruiting
                if days in (20, 25, 30, 45, 60):
                    split_frac = 0.5
                else:
                    split_frac = 0.0
            elif fp > 20 and fn <= 20:  # Phosphatic dominant (DAP, SSP, MAP)
                split_frac = p_pct / 100.0
            elif fk > 30 and fn <= 15:  # Potassic dominant (MOP, SOP)
                split_frac = k_pct / 100.0
            elif fn > 30 and fp <= 5 and fk <= 5:  # Nitrogenous dominant (Urea)
                split_frac = n_pct / 100.0
            else:  # Complex NPK
                denom = max(1.0, fn + fp + fk)
                split_frac = ((fn * n_pct) + (fp * p_pct) + (fk * k_pct)) / (100.0 * denom)

            if split_frac <= 0.01:
                continue

            stage_dose_ha = round(total_dose_ha * split_frac, 1)
            stage_total_kg = round(stage_dose_ha * area_ha, 1)

            if stage_total_kg <= 0.05:
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
            'weather_note': 'Ensure adequate soil moisture before broadcasting. Avoid foliar spray under strong wind (>18 km/h).'
        })

    return schedule_output


def _get_default_crop_family_schedule(crop: str) -> list:
    """Return distinct crop-family growth stage schedules."""
    is_legume = any(l in crop for l in LEGUMES)
    is_cereal = any(c in crop for c in CEREALS)

    if is_legume:
        return [
            {
                'stage': 'Land Prep & Seed Inoculation',
                'stage_order': 1, 'days_after_sowing': 0,
                'N_split_pct': 30.0, 'P_split_pct': 100.0, 'K_split_pct': 50.0,
                'application_method': 'Soil Incorporation & Seed Treatment',
                'instructions': 'Treat seed with Rhizobium culture. Apply full SSP + MOP + 50% Gypsum at land prep.'
            },
            {
                'stage': 'Active Vegetative (20-25 DAS)',
                'stage_order': 2, 'days_after_sowing': 25,
                'N_split_pct': 40.0, 'P_split_pct': 0.0, 'K_split_pct': 0.0,
                'application_method': 'Intercultivation & Light Top Dressing',
                'instructions': 'Apply light Nitrogen top-dressing only if nodulation is weak; perform weeding.'
            },
            {
                'stage': 'Flowering & Peg Formation (40-45 DAS)',
                'stage_order': 3, 'days_after_sowing': 45,
                'N_split_pct': 30.0, 'P_split_pct': 0.0, 'K_split_pct': 50.0,
                'application_method': 'Soil Top Dressing & Foliar Boron Spray',
                'instructions': 'Apply remaining 50% Gypsum at pegging stage. Spray Solubor (0.1%) for flower retention.'
            },
            {
                'stage': 'Pod Development (65-70 DAS)',
                'stage_order': 4, 'days_after_sowing': 65,
                'N_split_pct': 0.0, 'P_split_pct': 0.0, 'K_split_pct': 0.0,
                'application_method': 'Foliar Spray & Soil Moisture Management',
                'instructions': 'Maintain light irrigation to ensure pod expansion and prevent shell cracking.'
            }
        ]
    elif is_cereal:
        return [
            {
                'stage': 'Basal / At Sowing',
                'stage_order': 1, 'days_after_sowing': 0,
                'N_split_pct': 50.0, 'P_split_pct': 100.0, 'K_split_pct': 50.0,
                'application_method': 'Basal Soil Placement',
                'instructions': 'Incorporate full Phosphatic dose (DAP/NPK) + 50% Nitrogen + 50% Potash at sowing.'
            },
            {
                'stage': 'Active Tillering / Knee-High (20-25 DAS)',
                'stage_order': 2, 'days_after_sowing': 22,
                'N_split_pct': 25.0, 'P_split_pct': 0.0, 'K_split_pct': 0.0,
                'application_method': 'Top Dressing after 1st Irrigation',
                'instructions': 'Top-dress 25% Nitrogen (Neem Coated Urea) immediately after first CRI irrigation.'
            },
            {
                'stage': 'Jointing & Panicle Initiation (45-50 DAS)',
                'stage_order': 3, 'days_after_sowing': 45,
                'N_split_pct': 25.0, 'P_split_pct': 0.0, 'K_split_pct': 50.0,
                'application_method': 'Top Dressing & Potash Spray',
                'instructions': 'Apply remaining 25% Urea + 50% Potash to support tiller retention and earhead development.'
            }
        ]
    else:
        return [
            {
                'stage': 'Basal / Planting',
                'stage_order': 1, 'days_after_sowing': 0,
                'N_split_pct': 35.0, 'P_split_pct': 100.0, 'K_split_pct': 35.0,
                'application_method': 'Soil Placement',
                'instructions': 'Incorporate NPK complex + organic manure into soil prior to planting.'
            },
            {
                'stage': 'Vegetative Branching (30 DAS)',
                'stage_order': 2, 'days_after_sowing': 30,
                'N_split_pct': 35.0, 'P_split_pct': 0.0, 'K_split_pct': 30.0,
                'application_method': 'Side Dressing / Fertigation',
                'instructions': 'Side-dress 35% Nitrogen + 30% Potash around root zone.'
            },
            {
                'stage': 'Flowering & Fruit/Boll Formation (60 DAS)',
                'stage_order': 3, 'days_after_sowing': 60,
                'N_split_pct': 30.0, 'P_split_pct': 0.0, 'K_split_pct': 35.0,
                'application_method': 'Foliar Spray & Soil Fertigation',
                'instructions': 'Apply final split dose of Nitrogen & Potash; spray 19-19-19 WSF for fruit development.'
            }
        ]
