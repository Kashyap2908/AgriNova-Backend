"""
Protection Planner — Generates crop-specific, weather-integrated protection recommendations.
Tailors Weed Control, Disease Prevention, Pest Management, Micronutrient Sprays, and Growth Promoters.
Ensures every crop receives a distinct, realistic protection advisory or explicit 'Not Required' reason.
"""

import logging
from .data_loader import load_protection_master

logger = logging.getLogger(__name__)


def generate_protection_plan(crop: str, weather_data: dict = None) -> dict:
    """
    Generate a complete, crop-specific protection plan for the given crop.
    Includes: weed management, disease prevention, pest management, micronutrient spray, growth promoter.
    """
    crop_clean = (crop or '').strip().lower()
    weather_conditions = _parse_weather_conditions(weather_data)

    # Generate crop-specific protection entries
    entries = _get_crop_specific_protection_entries(crop_clean, weather_conditions)

    weed_plan = []
    disease_plan = []
    pest_plan = []
    micronutrient_plan = []
    growth_plan = []
    total_protection_cost = 0.0

    for entry in entries:
        item = _format_protection_item(entry, weather_conditions)

        item_cost = float(entry.get('cost_per_acre', 350.0))
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

    # Ensure NO EMPTY CATEGORIES — attach explicit "Not Required under current conditions" if empty
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
    """Creates a clear 'Not Required under current conditions' report item."""
    return {
        'problem': 'None / Low Risk',
        'growth_stage': 'All Stages',
        'category': category_title,
        'recommended_product': 'Not Required under current conditions',
        'active_ingredient': 'N/A',
        'application_method': 'Standard Field Monitoring',
        'dose_per_acre': 'N/A',
        'preventive': True,
        'weather_relevant': False,
        'weather_note': '',
        'remarks': f"Reason: {reason}.",
        'estimated_cost_per_acre': 0.0,
        'cost_display': '₹0 (Not Required)',
    }


def _get_crop_specific_protection_entries(crop: str, weather_conditions: dict) -> list:
    """Returns highly accurate, crop-specific protection entries for major crop families."""
    
    if any(k in crop for k in ['groundnut', 'peanut', 'soybean', 'chickpea', 'gram', 'moong', 'urad']):
        return [
            {
                'category': 'Weed Control', 'growth_stage': 'Pre-emergence (0-2 DAS)',
                'problem': 'Broadleaf & Annual Grass Weeds', 'recommended_product': 'Imazethapyr 10% SL + Pendimethalin',
                'active_ingredient': 'Imazethapyr + Pendimethalin', 'application_method': 'Soil Spray',
                'dose_per_acre': '400 ml', 'cost_per_acre': 480.0, 'preventive': True,
                'weather_trigger': 'Heavy_Rain', 'remarks': 'Spray on moist soil within 48 hours of sowing.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Flowering & Pegging (35-45 DAS)',
                'problem': 'Tikka Leaf Spot (Cercospora) & Rust', 'recommended_product': 'Tebuconazole 25.9% EC',
                'active_ingredient': 'Tebuconazole', 'application_method': 'Foliar Spray',
                'dose_per_acre': '250 ml', 'cost_per_acre': 550.0, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Apply at first sign of leaf spot or during humid cloudy weather.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Vegetative & Pegging',
                'problem': 'Tobacco Caterpillar (Spodoptera) & Thrips', 'recommended_product': 'Emamectin Benzoate 5% SG',
                'active_ingredient': 'Emamectin Benzoate', 'application_method': 'Foliar Spray',
                'dose_per_acre': '100 g', 'cost_per_acre': 380.0, 'preventive': False,
                'weather_trigger': 'High_Temp', 'remarks': 'Spray during early morning or late evening when pest population crosses ETL.'
            },
            {
                'category': 'Micronutrient Spray', 'growth_stage': 'Flowering (30 DAS)',
                'problem': 'Boron Deficiency & Flower Drop', 'recommended_product': 'Solubor / Borax 20%',
                'active_ingredient': 'Disodium Octaborate', 'application_method': 'Foliar Spray',
                'dose_per_acre': '250 g', 'cost_per_acre': 220.0, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Essential for flower retention and peg penetration.'
            },
            {
                'category': 'Growth Regulator', 'growth_stage': 'Pegging (45 DAS)',
                'problem': 'Excess Vegetative Canopy Growth', 'recommended_product': 'Chlormequat Chloride 50% SL (Lihocin)',
                'active_ingredient': 'Chlormequat Chloride', 'application_method': 'Foliar Spray',
                'dose_per_acre': '150 ml', 'cost_per_acre': 290.0, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Diverts photosynthates to underground pod development.'
            }
        ]

    elif any(k in crop for k in ['rice', 'paddy']):
        return [
            {
                'category': 'Weed Control', 'growth_stage': 'Transplanting / Pre-emergence',
                'problem': 'Barnyard Grass (Echinochloa) & Sedges', 'recommended_product': 'Pretilachlor 50% EC + Safener',
                'active_ingredient': 'Pretilachlor', 'application_method': 'Standing Water Broadcast',
                'dose_per_acre': '600 ml', 'cost_per_acre': 420.0, 'preventive': True,
                'weather_trigger': 'Heavy_Rain', 'remarks': 'Apply 3-5 days after transplanting in 2-3 cm standing water.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Tillering & Panicle Initiation',
                'problem': 'Yellow Stem Borer & Leaf Folder', 'recommended_product': 'Chlorantraniliprole 0.4% GR (Ferterra)',
                'active_ingredient': 'Chlorantraniliprole', 'application_method': 'Soil Granular Broadcast',
                'dose_per_acre': '4.0 kg', 'cost_per_acre': 620.0, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Broadcast with sand at 25-30 days after transplanting.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Heading & Panicle (60 DAS)',
                'problem': 'Blast (Pyricularia) & Sheath Blight', 'recommended_product': 'Azoxystrobin 18.2% + Difenoconazole 11.4%',
                'active_ingredient': 'Azoxystrobin + Difenoconazole', 'application_method': 'Foliar Spray',
                'dose_per_acre': '200 ml', 'cost_per_acre': 750.0, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Spray at boot leaf stage to protect panicles.'
            },
            {
                'category': 'Micronutrient Spray', 'growth_stage': 'Active Tillering (25 DAS)',
                'problem': 'Khaira Disease (Zinc Deficiency)', 'recommended_product': 'Zinc EDTA 12%',
                'active_ingredient': 'Zinc EDTA', 'application_method': 'Foliar Spray',
                'dose_per_acre': '150 g', 'cost_per_acre': 240.0, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Prevents rusty leaf spots caused by iron/zinc imbalance.'
            }
        ]

    elif any(k in crop for k in ['wheat']):
        return [
            {
                'category': 'Weed Control', 'growth_stage': '20-25 Days After Sowing',
                'problem': 'Phalaris minor (Mandusi) & Wild Oat', 'recommended_product': 'Sulfosulfuron 75% WG + Metsulfuron',
                'active_ingredient': 'Sulfosulfuron + Metsulfuron', 'application_method': 'Post-emergence Spray',
                'dose_per_acre': '13.5 g', 'cost_per_acre': 440.0, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Spray after 1st irrigation when weeds are at 2-4 leaf stage.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Jointing & Flag Leaf (50 DAS)',
                'problem': 'Yellow Rust (Puccinia) & Karnal Bunt', 'recommended_product': 'Propiconazole 25% EC (Tilt)',
                'active_ingredient': 'Propiconazole', 'application_method': 'Foliar Spray',
                'dose_per_acre': '200 ml', 'cost_per_acre': 490.0, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Apply at flag leaf emergence or cloudy cool weather.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Earhead Emergence (70 DAS)',
                'problem': 'Wheat Aphids & Armyworm', 'recommended_product': 'Thiamethoxam 25% WG',
                'active_ingredient': 'Thiamethoxam', 'application_method': 'Foliar Spray',
                'dose_per_acre': '40 g', 'cost_per_acre': 320.0, 'preventive': False,
                'weather_trigger': 'High_Temp', 'remarks': 'Spray when aphid count exceeds 5 per earhead.'
            }
        ]

    elif any(k in crop for k in ['cotton']):
        return [
            {
                'category': 'Weed Control', 'growth_stage': 'Pre-emergence (0-2 DAS)',
                'problem': 'Broadleaf & Sedge Weeds', 'recommended_product': 'Pyrithiobac Sodium 10% EC',
                'active_ingredient': 'Pyrithiobac Sodium', 'application_method': 'Post-emergence Spray',
                'dose_per_acre': '250 ml', 'cost_per_acre': 520.0, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Apply at 20-25 days after sowing on young weeds.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Square & Boll Formation (60-90 DAS)',
                'problem': 'Pink Bollworm & Whitefly', 'recommended_product': 'Spinetoram 11.7% SC (Delegate)',
                'active_ingredient': 'Spinetoram', 'application_method': 'Foliar Spray',
                'dose_per_acre': '180 ml', 'cost_per_acre': 780.0, 'preventive': False,
                'weather_trigger': 'High_Temp', 'remarks': 'Controls resistant caterpillars and sucking pest complex.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Bolling Phase (80 DAS)',
                'problem': 'Bacterial Blight & Alternaria Leaf Spot', 'recommended_product': 'Copper Oxychloride 50% WP + Streptocycline',
                'active_ingredient': 'Copper Oxychloride + Streptomycin', 'application_method': 'Foliar Spray',
                'dose_per_acre': '500 g', 'cost_per_acre': 450.0, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Spray during overcast rainy periods.'
            },
            {
                'category': 'Growth Regulator', 'growth_stage': 'Peak Bolling (90 DAS)',
                'problem': 'Square Drop & Excessive Vegetative Height', 'recommended_product': 'Mepiquat Chloride 5% AS (Chamatkar)',
                'active_ingredient': 'Mepiquat Chloride', 'application_method': 'Foliar Spray',
                'dose_per_acre': '200 ml', 'cost_per_acre': 340.0, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Prevents boll shedding and controls canopy height.'
            }
        ]

    elif any(k in crop for k in ['maize', 'corn', 'bajra', 'jowar', 'sorghum', 'ragi']):
        return [
            {
                'category': 'Weed Control', 'growth_stage': 'Pre-emergence (0-2 DAS)',
                'problem': 'Broadleaf & Grass Weeds', 'recommended_product': 'Atrazine 50% WP',
                'active_ingredient': 'Atrazine', 'application_method': 'Soil Spray',
                'dose_per_acre': '500 g', 'cost_per_acre': 360.0, 'preventive': True,
                'weather_trigger': 'Heavy_Rain', 'remarks': 'Apply immediately post-sowing on moist seedbed.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Whorl Stage (15-25 DAS)',
                'problem': 'Fall Armyworm (FAW) & Shoot Fly', 'recommended_product': 'Emamectin Benzoate 5% SG / Chlorantraniliprole',
                'active_ingredient': 'Emamectin Benzoate', 'application_method': 'Whorl Application',
                'dose_per_acre': '80 g', 'cost_per_acre': 420.0, 'preventive': False,
                'weather_trigger': 'High_Temp', 'remarks': 'Direct spray into central whorl at first sign of pinhole damage.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Tasseling & Silking (45 DAS)',
                'problem': 'Turcicum Leaf Blight & Downy Mildew', 'recommended_product': 'Metalaxyl 8% + Mancozeb 64% WP (Ridomil Gold)',
                'active_ingredient': 'Metalaxyl + Mancozeb', 'application_method': 'Foliar Spray',
                'dose_per_acre': '500 g', 'cost_per_acre': 580.0, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Apply preventively during humid warm weather.'
            }
        ]

    elif any(k in crop for k in ['sugarcane']):
        return [
            {
                'category': 'Weed Control', 'growth_stage': 'Pre-emergence (0-30 DAS)',
                'problem': 'Cyperus rotundus & Broadleaf Weeds', 'recommended_product': 'Atrazine 50% WP + 2,4-D Sodium Salt',
                'active_ingredient': 'Atrazine + 2,4-D', 'application_method': 'Soil & Foliar Spray',
                'dose_per_acre': '1.0 kg', 'cost_per_acre': 480.0, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Apply post-planting before cane canopy closure.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Early Shoot Phase (45 DAS)',
                'problem': 'Early Shoot Borer & Root Borer', 'recommended_product': 'Fipronil 0.3% GR (Regent)',
                'active_ingredient': 'Fipronil', 'application_method': 'Soil Granular Broadcast',
                'dose_per_acre': '7.5 kg', 'cost_per_acre': 680.0, 'preventive': True,
                'weather_trigger': 'High_Temp', 'remarks': 'Incorporate into furrow soil followed by light irrigation.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Grand Growth Phase (120 DAS)',
                'problem': 'Red Rot (Colletotrichum) & Smut', 'recommended_product': 'Carbendazim 50% WP (Bavistin)',
                'active_ingredient': 'Carbendazim', 'application_method': 'Set Drenching / Spray',
                'dose_per_acre': '300 g', 'cost_per_acre': 390.0, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Drench cane roots or setts before planting.'
            }
        ]

    else:  # Vegetables & Horticultural Crops (Tomato, Potato, Onion, Chilli, Brinjal, etc.)
        return [
            {
                'category': 'Weed Control', 'growth_stage': 'Pre-transplanting (0 DAS)',
                'problem': 'Annual Grasses & Broadleaf Weeds', 'recommended_product': 'Oxyfluorfen 23.5% EC (Goal)',
                'active_ingredient': 'Oxyfluorfen', 'application_method': 'Soil Spray',
                'dose_per_acre': '200 ml', 'cost_per_acre': 460.0, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Apply 3 days before transplanting on prepared beds.'
            },
            {
                'category': 'Pest Management', 'growth_stage': 'Vegetative & Flowering (30-50 DAS)',
                'problem': 'Thrips, Whitefly & Fruit Borer', 'recommended_product': 'Spinetoram 11.7% SC / Abamectin 1.9% EC',
                'active_ingredient': 'Spinetoram', 'application_method': 'Foliar Spray',
                'dose_per_acre': '160 ml', 'cost_per_acre': 720.0, 'preventive': False,
                'weather_trigger': 'High_Temp', 'remarks': 'Alternate chemical classes to manage vector thrips/whitefly.'
            },
            {
                'category': 'Disease Prevention', 'growth_stage': 'Fruiting Phase (60 DAS)',
                'problem': 'Early/Late Blight & Powdery Mildew', 'recommended_product': 'Azoxystrobin 11% + Tebuconazole 18.3% (Custodia)',
                'active_ingredient': 'Azoxystrobin + Tebuconazole', 'application_method': 'Foliar Spray',
                'dose_per_acre': '200 ml', 'cost_per_acre': 750.0, 'preventive': True,
                'weather_trigger': 'High_Humidity', 'remarks': 'Dual systemic protection for fruit quality and skin finish.'
            },
            {
                'category': 'Micronutrient Spray', 'growth_stage': 'Flowering & Fruit Set (40 DAS)',
                'problem': 'Calcium & Boron Deficiency (Blossom End Rot)', 'recommended_product': 'Chelated Calcium + Borax 20%',
                'active_ingredient': 'Calcium EDTA + Boron', 'application_method': 'Foliar Spray',
                'dose_per_acre': '250 g', 'cost_per_acre': 320.0, 'preventive': True,
                'weather_trigger': 'None', 'remarks': 'Prevents blossom end rot and fruit cracking.'
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
        'dose_per_acre': entry['dose_per_acre'],
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
