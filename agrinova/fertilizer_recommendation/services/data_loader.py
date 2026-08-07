"""
Data Loader Service — Cached CSV readers for all Nutrition & Protection datasets.
Loads data once into memory on first access and serves subsequent reads from cache.
"""

import csv
import os
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

BASE_DIR = getattr(settings, 'BASE_DIR', Path(__file__).resolve().parent.parent.parent)
DATA_DIR = Path(BASE_DIR).parent / 'ml' / 'data'
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'ml' / 'data'

# Module-level caches
_fertilizer_master_cache = None
_crop_nutrient_cache = None
_growth_stage_cache = None
_protection_cache = None


def _safe_float(value, default=0.0):
    """Safely convert a value to float."""
    try:
        return float(value) if value not in (None, '', 'None', 'N/A') else default
    except (ValueError, TypeError):
        return default


def _load_csv(filepath):
    """Read a CSV file and return list of dicts."""
    rows = []
    if not os.path.exists(filepath):
        logger.error(f"CSV file not found: {filepath}")
        return rows
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row:
                    rows.append(row)
    except Exception as e:
        logger.error(f"Error reading CSV {filepath}: {e}")
    return rows


def load_fertilizer_master():
    """Load and cache the fertilizer master catalog."""
    global _fertilizer_master_cache
    if _fertilizer_master_cache is not None:
        return _fertilizer_master_cache

    raw = _load_csv(DATA_DIR / 'fertilizer_master.csv')
    catalog = []
    for row in raw:
        name = (row.get('Fertilizer_Name') or '').strip()
        if not name:
            continue
        catalog.append({
            'name': name,
            'type': (row.get('Fertilizer_Type') or '').strip(),
            'brand': (row.get('Brand') or '').strip(),
            'N_pct': _safe_float(row.get('N_pct')),
            'P_pct': _safe_float(row.get('P_pct')),
            'K_pct': _safe_float(row.get('K_pct')),
            'S_pct': _safe_float(row.get('S_pct')),
            'Zn_pct': _safe_float(row.get('Zn_pct')),
            'B_pct': _safe_float(row.get('B_pct')),
            'Ca_pct': _safe_float(row.get('Ca_pct')),
            'Mg_pct': _safe_float(row.get('Mg_pct')),
            'Organic_Carbon_pct': _safe_float(row.get('Organic_Carbon_pct')),
            'other_micronutrients': (row.get('Other_Micronutrients') or '').strip(),
            'application_method': (row.get('Application_Method') or '').strip(),
            'suitable_crops': (row.get('Suitable_Crops') or 'All').strip(),
            'suitable_soil_types': (row.get('Suitable_Soil_Types') or 'All').strip(),
            'suitable_seasons': (row.get('Suitable_Seasons') or 'All').strip(),
            'water_compatibility': (row.get('Water_Compatibility') or 'Both').strip(),
            'cost_per_kg': _safe_float(row.get('Cost_Per_Kg_INR')),
            'unit': (row.get('Unit') or 'kg').strip(),
            'availability': (row.get('Availability') or 'Medium').strip(),
            'remarks': (row.get('Remarks') or '').strip(),
        })
    _fertilizer_master_cache = catalog
    logger.info(f"Loaded {len(catalog)} fertilizers from master catalog")
    return catalog


def load_crop_nutrient_requirements():
    """Load and cache the crop nutrient requirement dataset, indexed by crop name."""
    global _crop_nutrient_cache
    if _crop_nutrient_cache is not None:
        return _crop_nutrient_cache

    raw = _load_csv(DATA_DIR / 'crop_nutrient_requirement.csv')
    requirements = {}
    for row in raw:
        crop = (row.get('Crop') or '').strip().lower()
        if not crop:
            continue
        if crop not in requirements:
            requirements[crop] = []
        requirements[crop].append({
            'season': (row.get('Season') or 'All').strip(),
            'stage': (row.get('Growth_Stage') or '').strip(),
            'N': _safe_float(row.get('N_kg_ha')),
            'P': _safe_float(row.get('P_kg_ha')),
            'K': _safe_float(row.get('K_kg_ha')),
            'S': _safe_float(row.get('S_kg_ha')),
            'Zn': _safe_float(row.get('Zn_kg_ha')),
            'B': _safe_float(row.get('B_kg_ha')),
            'pH_min': _safe_float(row.get('Ideal_pH_Min'), 6.0),
            'pH_max': _safe_float(row.get('Ideal_pH_Max'), 7.5),
            'source': (row.get('Source') or '').strip(),
        })
    _crop_nutrient_cache = requirements
    logger.info(f"Loaded nutrient requirements for {len(requirements)} crops")
    return requirements


def load_growth_stage_schedule():
    """Load and cache the crop growth stage schedule, indexed by crop name."""
    global _growth_stage_cache
    if _growth_stage_cache is not None:
        return _growth_stage_cache

    raw = _load_csv(DATA_DIR / 'crop_growth_stage_schedule.csv')
    schedules = {}
    for row in raw:
        crop = (row.get('Crop') or '').strip().lower()
        if not crop:
            continue
        if crop not in schedules:
            schedules[crop] = []
        schedules[crop].append({
            'stage': (row.get('Stage') or '').strip(),
            'stage_order': int(_safe_float(row.get('Stage_Order'), 1)),
            'days_after_sowing': int(_safe_float(row.get('Days_After_Sowing'), 0)),
            'N_split_pct': _safe_float(row.get('N_Split_Pct')),
            'P_split_pct': _safe_float(row.get('P_Split_Pct')),
            'K_split_pct': _safe_float(row.get('K_Split_Pct')),
            'application_method': (row.get('Application_Method') or '').strip(),
            'instructions': (row.get('Instructions') or '').strip(),
        })
    # Sort stages by order
    for crop_key in schedules:
        schedules[crop_key].sort(key=lambda s: s['stage_order'])

    _growth_stage_cache = schedules
    logger.info(f"Loaded growth stage schedules for {len(schedules)} crops")
    return schedules


def load_protection_master():
    """Load and cache the crop protection master dataset, indexed by crop name."""
    global _protection_cache
    if _protection_cache is not None:
        return _protection_cache

    raw = _load_csv(DATA_DIR / 'crop_protection_master.csv')
    protection = {}
    for row in raw:
        crop = (row.get('Crop') or '').strip().lower()
        if not crop:
            continue
        if crop not in protection:
            protection[crop] = []
        protection[crop].append({
            'category': (row.get('Category') or '').strip(),
            'growth_stage': (row.get('Growth_Stage') or '').strip(),
            'problem': (row.get('Problem') or '').strip(),
            'recommended_product': (row.get('Recommended_Product') or '').strip(),
            'active_ingredient': (row.get('Active_Ingredient') or '').strip(),
            'application_method': (row.get('Application_Method') or '').strip(),
            'dose_per_acre': (row.get('Dose_Per_Acre') or '').strip(),
            'cost_per_unit': _safe_float(row.get('Cost_Per_Unit_INR')),
            'unit': (row.get('Unit') or '').strip(),
            'preventive': (row.get('Preventive') or '').strip().lower() == 'yes',
            'weather_trigger': (row.get('Weather_Trigger') or 'None').strip(),
            'remarks': (row.get('Remarks') or '').strip(),
        })
    _protection_cache = protection
    logger.info(f"Loaded protection data for {len(protection)} crops")
    return protection


def clear_all_caches():
    """Clear all dataset caches (useful for testing)."""
    global _fertilizer_master_cache, _crop_nutrient_cache, _growth_stage_cache, _protection_cache
    _fertilizer_master_cache = None
    _crop_nutrient_cache = None
    _growth_stage_cache = None
    _protection_cache = None


def load_crop_list():
    """Return sorted unique list of crop names from nutrient requirements dataset."""
    crop_names = set()
    raw_data = _load_csv(DATA_DIR / 'crop_nutrient_requirement.csv')
    for row in raw_data:
        c = (row.get('Crop') or '').strip()
        if c:
            crop_names.add(c)
    return sorted(list(crop_names))

