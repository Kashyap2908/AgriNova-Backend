"""
Nutrient Planner — Looks up crop nutrient requirements and computes total nutrient gap.
Reads from crop_nutrient_requirement.csv via data_loader.
"""

import re
import logging
from .data_loader import load_crop_nutrient_requirements

logger = logging.getLogger(__name__)


def get_crop_requirement(crop: str, season: str = 'All') -> dict:
    """
    Look up total crop nutrient requirement (kg/ha) across all growth stages.
    Returns: {'N': float, 'P': float, 'K': float, 'S': float, 'Zn': float, 'B': float,
              'pH_min': float, 'pH_max': float, 'stages': list, 'source': str}
    """
    requirements = load_crop_nutrient_requirements()
    crop_clean = (crop or '').strip().lower()
    season_clean = (season or 'All').strip().lower()

    # Priority 1: Exact match
    matched_stages = requirements.get(crop_clean)

    # Priority 2: Word boundary match
    if not matched_stages:
        pattern = r'\b' + re.escape(crop_clean) + r'\b'
        for c_key, stages in requirements.items():
            if re.search(pattern, c_key):
                matched_stages = stages
                break

    # Priority 3: Substring match
    if not matched_stages:
        for c_key, stages in requirements.items():
            if c_key in crop_clean or crop_clean in c_key:
                matched_stages = stages
                break

    # Priority 4: Default fallback
    if not matched_stages:
        matched_stages = requirements.get('default', [
            {'stage': 'Basal', 'N': 40.0, 'P': 40.0, 'K': 30.0, 'S': 0.0, 'Zn': 0.0, 'B': 0.0,
             'pH_min': 6.0, 'pH_max': 7.5, 'season': 'All', 'source': 'ICAR General'},
            {'stage': 'Vegetative', 'N': 30.0, 'P': 0.0, 'K': 0.0, 'S': 0.0, 'Zn': 0.0, 'B': 0.0,
             'pH_min': 6.0, 'pH_max': 7.5, 'season': 'All', 'source': 'ICAR General'},
            {'stage': 'Flowering', 'N': 20.0, 'P': 20.0, 'K': 30.0, 'S': 0.0, 'Zn': 0.0, 'B': 0.0,
             'pH_min': 6.0, 'pH_max': 7.5, 'season': 'All', 'source': 'ICAR General'},
        ])

    # Filter by season if not 'all'
    if season_clean != 'all':
        season_filtered = [s for s in matched_stages if s['season'].strip().lower() in (season_clean, 'all')]
        if season_filtered:
            matched_stages = season_filtered

    total_n = sum(s['N'] for s in matched_stages)
    total_p = sum(s['P'] for s in matched_stages)
    total_k = sum(s['K'] for s in matched_stages)
    total_s = sum(s.get('S', 0) for s in matched_stages)
    total_zn = sum(s.get('Zn', 0) for s in matched_stages)
    total_b = sum(s.get('B', 0) for s in matched_stages)
    ph_min = matched_stages[0].get('pH_min', 6.0) if matched_stages else 6.0
    ph_max = matched_stages[0].get('pH_max', 7.5) if matched_stages else 7.5
    source = matched_stages[0].get('source', 'ICAR General') if matched_stages else 'ICAR General'

    return {
        'N': round(total_n, 1),
        'P': round(total_p, 1),
        'K': round(total_k, 1),
        'S': round(total_s, 1),
        'Zn': round(total_zn, 1),
        'B': round(total_b, 1),
        'pH_min': ph_min,
        'pH_max': ph_max,
        'stages': matched_stages,
        'source': source,
    }


def compute_nutrient_gap(crop_requirement: dict, soil_nutrients: dict) -> dict:
    """
    Compute the net nutrient gap (deficiency) between crop requirement and soil available nutrients.
    Returns deficiency dict for each nutrient.
    """
    from .soil_analyzer import calculate_deficiency
    return calculate_deficiency(crop_requirement, soil_nutrients)
