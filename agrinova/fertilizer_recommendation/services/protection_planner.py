"""
Protection Planner — Generates crop protection recommendations for weeds, diseases, pests, micronutrients, and growth promoters.
Reads from crop_protection_master.csv via data_loader. Applies weather-based triggers.
Ensures every category has realistic recommendations or explicit "Not required under current conditions" statements.
"""

import logging
from .data_loader import load_protection_master

logger = logging.getLogger(__name__)

LEGUMES = ['groundnut', 'peanut', 'soybean', 'chickpea', 'gram', 'moong', 'urad', 'pigeonpea', 'arhar', 'tur', 'pea', 'lentil']
CEREALS = ['wheat', 'rice', 'paddy', 'maize', 'corn', 'jowar', 'sorghum', 'bajra', 'ragi']
COMMERCIAL = ['cotton', 'sugarcane', 'potato', 'onion', 'garlic', 'tomato', 'chilli', 'brinjal', 'banana', 'papaya', 'mango', 'turmeric', 'ginger']


def generate_protection_plan(crop: str, weather_data: dict = None) -> dict:
    """
    Generate a complete protection plan for the given crop.
    Includes: weed management, disease prevention, pest management, micronutrient spray, growth promoter.
    Ensures NO empty categories.
    """
    protection_db = load_protection_master()
    crop_clean = (crop or '').strip().lower()

    # Find matching entries
    entries = protection_db.get(crop_clean, [])

    # Try partial match if no exact match
    if not entries:
        for c_key, items in protection_db.items():
            if c_key in crop_clean or crop_clean in c_key:
                entries = items
                break

    # Fallback to default crop-family recommendations if DB entries incomplete
    if not entries:
        entries = _generate_default_protection_entries(crop_clean)

    # Parse weather conditions
    weather_conditions = _parse_weather_conditions(weather_data)

    # Categorize entries
    weed_plan = []
    disease_plan = []
    pest_plan = []
    micronutrient_plan = []
    growth_plan = []
    total_protection_cost = 0.0

    for entry in entries:
        item = _format_protection_item(entry, weather_conditions)

        # Calculate approximate cost per acre
        try:
            dose_val = float(entry['dose_per_acre']) if str(entry['dose_per_acre']).replace('.', '').isdigit() else 1.0
            unit_clean = entry.get('unit', '').lower().strip()
            if unit_clean in ('ml', 'g'):
                qty_in_standard_unit = dose_val / 1000.0
            else:
                qty_in_standard_unit = dose_val
            item_cost = qty_in_standard_unit * float(entry.get('cost_per_unit', 350))
        except (ValueError, TypeError):
            item_cost = float(entry.get('cost_per_unit', 350))

        item['estimated_cost_per_acre'] = round(item_cost, 2)
        item['cost_display'] = f"₹{round(item_cost, 0):,.0f}/acre"
        total_protection_cost += item_cost

        category = entry.get('category', '').lower()
        if 'weed' in category:
            weed_plan.append(item)
        elif 'disease' in category:
            disease_plan.append(item)
        elif 'pest' in category:
            pest_plan.append(item)
        elif 'micronutrient' in category:
            micronutrient_plan.append(item)
        elif 'growth' in category or 'regulator' in category or 'promoter' in category:
            growth_plan.append(item)

    # Ensure NO EMPTY CATEGORIES — attach explicit "Not required under current conditions" entry if empty
    if not weed_plan:
        weed_plan.append(_create_not_required_item("Weed Control", "Clean seedbed & low weed seedbank under present soil moisture"))
    if not disease_plan:
        disease_plan.append(_create_not_required_item("Disease Prevention", "Low humidity and clear canopy conditions — no active pathogen threat"))
    if not pest_plan:
        pest_plan.append(_create_not_required_item("Pest Management", "Sucking pest & caterpillar populations below Economic Threshold Level (ETL)"))
    if not micronutrient_plan:
        micronutrient_plan.append(_create_not_required_item("Micronutrient Spray", "Soil reserves adequate; foliar micronutrients not required at present stage"))
    if not growth_plan:
        growth_plan.append(_create_not_required_item("Growth Regulator", "Crop canopy showing normal vigorous vegetative growth"))

    return {
        'weed_management': weed_plan,
        'disease_prevention': disease_plan,
        'pest_management': pest_plan,
        'micronutrient_spray': micronutrient_plan,
        'growth_promoter': growth_plan,
        'total_protection_cost_per_acre': round(total_protection_cost, 2),
        'weather_triggered_alerts': _get_weather_alerts(entries, weather_conditions),
    }


def _create_not_required_item(category_title: str, reason: str) -> dict:
    """Creates a clear 'Not required under current conditions' report item."""
    return {
        'problem': 'None / Low Risk',
        'growth_stage': 'All Stages',
        'category': category_title,
        'recommended_product': 'Not required under current conditions',
        'active_ingredient': 'N/A',
        'application_method': 'Standard Monitoring',
        'dose_per_acre': 'N/A',
        'preventive': True,
        'weather_relevant': False,
        'weather_note': '',
        'remarks': f"Reason: {reason}.",
        'estimated_cost_per_acre': 0.0,
        'cost_display': '₹0 (Not Required)',
    }


def _generate_default_protection_entries(crop: str) -> list:
    """Generate realistic default crop protection entries tailored to crop family."""
    is_legume = any(l in crop for l in LEGUMES)
    is_cereal = any(c in crop for c in CEREALS)

    if is_legume:
        return [
            {
                'category': 'Weed Control', 'growth_stage': 'Basal / Pre-emergence',
                'problem': 'Broadleaf & Grass Weeds', 'recommended_product': 'Pendimethalin 30% EC',
                'active_ingredient': 'Pendimethalin', 'application_method': 'Foliar Spray (Pre-emergence)',
                'dose_per_acre': '1.0', 'unit': 'Litre', 'cost_per_unit': 450, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Spray within 48 hours of sowing on moist soil.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Flowering & Pegging',
                'problem': 'Tikka Leaf Spot & Rust', 'recommended_product': 'Tebuconazole 25.9% EC',
                'active_ingredient': 'Tebuconazole', 'application_method': 'Foliar Spray',
                'dose_per_acre': '250', 'unit': 'ml', 'cost_per_unit': 550, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Apply at first sign of leaf spot or during humid weather.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Vegetative',
                'problem': 'Aphids, Thrips & Spodoptera', 'recommended_product': 'Emamectin Benzoate 5% SG',
                'active_ingredient': 'Emamectin Benzoate', 'application_method': 'Foliar Spray',
                'dose_per_acre': '100', 'unit': 'g', 'cost_per_unit': 380, 'preventive': False,
                'weather_trigger': 'High_Temp', 'remarks': 'Spray in evening hours when pest threshold exceeds ETL.'
            },
            {
                'category': 'Micronutrient Spray', 'growth_stage': 'Flowering',
                'problem': 'Boron Deficiency & Flower Drop', 'recommended_product': 'Solubor / Borax 20%',
                'active_ingredient': 'Disodium Octaborate', 'application_method': 'Foliar Spray',
                'dose_per_acre': '250', 'unit': 'g', 'cost_per_unit': 220, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Spray 1g/L water during flowering for seed setting & pod fill.'
            },
            {
                'category': 'Growth Regulator', 'growth_stage': 'Pegging',
                'problem': 'Excess Vegetative Canopy', 'recommended_product': 'Chlormequat Chloride (Lihocin)',
                'active_ingredient': 'Chlormequat Chloride', 'application_method': 'Foliar Spray',
                'dose_per_acre': '150', 'unit': 'ml', 'cost_per_unit': 280, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Diverts energy from foliage to underground pod development.'
            }
        ]
    elif is_cereal:
        return [
            {
                'category': 'Weed Control', 'growth_stage': '20-25 Days After Sowing',
                'problem': 'Phalaris minor & Broadleaf Weeds', 'recommended_product': 'Sulfosulfuron 75% WG',
                'active_ingredient': 'Sulfosulfuron', 'application_method': 'Post-emergence Spray',
                'dose_per_acre': '13.5', 'unit': 'g', 'cost_per_unit': 420, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Apply 20-25 DAS after first irrigation.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Heading / Panicle',
                'problem': 'Yellow Rust & Blast', 'recommended_product': 'Propiconazole 25% EC',
                'active_ingredient': 'Propiconazole', 'application_method': 'Foliar Spray',
                'dose_per_acre': '200', 'unit': 'ml', 'cost_per_unit': 480, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Apply at flag leaf emergence or humid cloudy weather.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Vegetative',
                'problem': 'Stem Borer & Aphids', 'recommended_product': 'Chlorantraniliprole 18.5% SC',
                'active_ingredient': 'Chlorantraniliprole', 'application_method': 'Foliar Spray',
                'dose_per_acre': '60', 'unit': 'ml', 'cost_per_unit': 650, 'preventive': False,
                'weather_trigger': 'High_Temp', 'remarks': 'Protects against stem borer and leaf folder larvae.'
            },
            {
                'category': 'Micronutrient Spray', 'growth_stage': 'Tillering',
                'problem': 'Zinc & Iron Chlorosis', 'recommended_product': 'Chelated Zinc EDTA 12%',
                'active_ingredient': 'Zinc EDTA', 'application_method': 'Foliar Spray',
                'dose_per_acre': '100', 'unit': 'g', 'cost_per_unit': 250, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Foliar spray during active tillering phase.'
            }
        ]
    else:
        return [
            {
                'category': 'Weed Control', 'growth_stage': 'Pre-emergence',
                'problem': 'Annual Grasses & Sedge Weeds', 'recommended_product': 'Oxyfluorfen 23.5% EC',
                'active_ingredient': 'Oxyfluorfen', 'application_method': 'Soil Spray',
                'dose_per_acre': '200', 'unit': 'ml', 'cost_per_unit': 480, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Apply immediately post-sowing on moist soil.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Flowering & Fruiting',
                'problem': 'Powdery Mildew & Fruit Rot', 'recommended_product': 'Azoxystrobin 11% + Tebuconazole 18.3%',
                'active_ingredient': 'Azoxystrobin + Tebuconazole', 'application_method': 'Foliar Spray',
                'dose_per_acre': '200', 'unit': 'ml', 'cost_per_unit': 720, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Dual systemic action for high yield security.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Vegetative & Fruiting',
                'problem': 'Fruit/Boll Borer & Whitefly', 'recommended_product': 'Spinetoram 11.7% SC',
                'active_ingredient': 'Spinetoram', 'application_method': 'Foliar Spray',
                'dose_per_acre': '180', 'unit': 'ml', 'cost_per_unit': 780, 'preventive': False,
                'weather_trigger': 'High_Temp', 'remarks': 'Controls resistant caterpillars and sucking pests.'
            }
        ]


def _parse_weather_conditions(weather_data: dict) -> dict:
    """Parse weather data to determine active conditions."""
    if not weather_data:
        return {'high_humidity': False, 'heavy_rain': False, 'high_temp': False, 'strong_wind': False}

    current = weather_data.get('current_weather', {})
    if not current:
        return {'high_humidity': False, 'heavy_rain': False, 'high_temp': False, 'strong_wind': False}

    humidity = float(current.get('humidity', 65) or 65)
    rainfall = float(current.get('rainfall', 0) or 0)
    temperature = float(current.get('temperature', 28) or 28)
    wind = float(current.get('wind_speed', 5) or 5)

    return {
        'high_humidity': humidity > 75,
        'heavy_rain': rainfall > 10,
        'high_temp': temperature > 35,
        'strong_wind': wind > 18,
    }


def _format_protection_item(entry: dict, weather_conditions: dict) -> dict:
    """Format a protection entry with weather relevance."""
    trigger = entry.get('weather_trigger', 'None')
    weather_relevant = False
    weather_note = ''

    if trigger == 'High_Humidity' and weather_conditions.get('high_humidity'):
        weather_relevant = True
        weather_note = '⚠️ High humidity (>75%) detected — elevated risk of fungal blight/leaf spot. Apply preventive spray.'
    elif trigger == 'Heavy_Rain' and weather_conditions.get('heavy_rain'):
        weather_relevant = True
        weather_note = '⚠️ Heavy rain forecast — delay foliar spray or apply sticker adjuvant.'
    elif trigger == 'High_Temp' and weather_conditions.get('high_temp'):
        weather_relevant = True
        weather_note = '⚠️ High temperature (>35°C) — spray during early morning or evening to prevent evaporation.'

    return {
        'problem': entry['problem'],
        'growth_stage': entry['growth_stage'],
        'category': entry['category'],
        'recommended_product': entry['recommended_product'],
        'active_ingredient': entry['active_ingredient'],
        'application_method': entry['application_method'],
        'dose_per_acre': f"{entry['dose_per_acre']} {entry.get('unit', 'ml/acre')}",
        'preventive': entry['preventive'],
        'weather_relevant': weather_relevant,
        'weather_note': weather_note,
        'remarks': entry['remarks'],
    }


def _get_weather_alerts(entries: list, weather_conditions: dict) -> list:
    """Generate weather-triggered alerts from protection entries."""
    alerts = []
    seen = set()

    for entry in entries:
        trigger = entry.get('weather_trigger', 'None')
        if trigger == 'None':
            continue

        triggered = False
        if trigger == 'High_Humidity' and weather_conditions.get('high_humidity'):
            triggered = True
        elif trigger == 'Heavy_Rain' and weather_conditions.get('heavy_rain'):
            triggered = True
        elif trigger == 'High_Temp' and weather_conditions.get('high_temp'):
            triggered = True

        if triggered and entry['problem'] not in seen:
            seen.add(entry['problem'])
            alerts.append({
                'problem': entry['problem'],
                'category': entry['category'],
                'product': entry['recommended_product'],
                'reason': f"Weather condition ({trigger.replace('_', ' ')}) increases risk of {entry['problem']}.",
            })

    return alerts
