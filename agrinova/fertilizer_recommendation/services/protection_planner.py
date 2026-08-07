"""
Protection Planner — Generates crop protection recommendations for weeds, diseases, pests, micronutrients, and growth promoters.
Reads from crop_protection_master.csv via data_loader. Applies weather-based triggers.
"""

import logging
from .data_loader import load_protection_master

logger = logging.getLogger(__name__)


def generate_protection_plan(crop: str, weather_data: dict = None) -> dict:
    """
    Generate a complete protection plan for the given crop.
    Includes: weed management, disease prevention, pest management, micronutrient spray, growth promoter.
    Weather triggers activate preventive recommendations.
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
            dose_val = float(entry['dose_per_acre']) if entry['dose_per_acre'].replace('.', '').isdigit() else 1.0
            unit_clean = entry.get('unit', '').lower().strip()
            if unit_clean in ('ml', 'g'):
                qty_in_standard_unit = dose_val / 1000.0
            else:
                qty_in_standard_unit = dose_val
            item_cost = qty_in_standard_unit * entry['cost_per_unit']
        except (ValueError, TypeError):
            item_cost = entry['cost_per_unit']

        item['estimated_cost_per_acre'] = round(item_cost, 2)
        item['cost_display'] = f"₹{round(item_cost, 0):,.0f}/acre"
        total_protection_cost += item_cost

        category = entry['category'].lower()
        if category == 'weed':
            weed_plan.append(item)
        elif category == 'disease':
            disease_plan.append(item)
        elif category == 'pest':
            pest_plan.append(item)
        elif category == 'micronutrient':
            micronutrient_plan.append(item)
        elif 'growth' in category or 'regulator' in category or 'promoter' in category:
            growth_plan.append(item)

    return {
        'weed_management': weed_plan,
        'disease_prevention': disease_plan,
        'pest_management': pest_plan,
        'micronutrient_spray': micronutrient_plan,
        'growth_promoter': growth_plan,
        'total_protection_cost_per_acre': round(total_protection_cost, 2),
        'weather_triggered_alerts': _get_weather_alerts(entries, weather_conditions),
    }


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
        'high_humidity': humidity > 80,
        'heavy_rain': rainfall > 10,
        'high_temp': temperature > 35,
        'strong_wind': wind > 20,
    }


def _format_protection_item(entry: dict, weather_conditions: dict) -> dict:
    """Format a protection entry with weather relevance."""
    trigger = entry.get('weather_trigger', 'None')
    weather_relevant = False
    weather_note = ''

    if trigger == 'High_Humidity' and weather_conditions.get('high_humidity'):
        weather_relevant = True
        weather_note = '⚠️ High humidity (>80%) detected — fungal disease risk elevated. Apply preventive spray.'
    elif trigger == 'Heavy_Rain' and weather_conditions.get('heavy_rain'):
        weather_relevant = True
        weather_note = '⚠️ Heavy rain forecast/detected — delay foliar spray or apply sticker adjuvant.'
    elif trigger == 'High_Temp' and weather_conditions.get('high_temp'):
        weather_relevant = True
        weather_note = '⚠️ High temperature (>35°C) — apply chemical in evening hours (after 4 PM) for maximum efficacy.'

    return {
        'problem': entry['problem'],
        'growth_stage': entry['growth_stage'],
        'category': entry['category'],
        'recommended_product': entry['recommended_product'],
        'active_ingredient': entry['active_ingredient'],
        'application_method': entry['application_method'],
        'dose_per_acre': f"{entry['dose_per_acre']} {entry['unit']}",
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
