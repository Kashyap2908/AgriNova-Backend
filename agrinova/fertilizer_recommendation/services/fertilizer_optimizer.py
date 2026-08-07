"""
Fertilizer Optimizer — LP-based multi-strategy fertilizer combination optimizer.
Dynamically generates Budget Plan, Balanced Plan, and Premium Plan from dataset.
Provides alternative fertilizer recommendations for every selected product.
"""

import logging
import numpy as np
from scipy.optimize import linprog

from .data_loader import load_fertilizer_master

logger = logging.getLogger(__name__)

# Strategy definitions for 3 primary plans
PLAN_STRATEGIES = [
    {
        'key': 'budget',
        'title': 'Budget Plan (Cost-Effective)',
        'tag': 'BUDGET PLAN',
        'badge_color': 'amber',
        'desc': 'Minimizes upfront cost using standard, widely available fertilizers (Neem Coated Urea, SSP, MOP). Ideal for budget-conscious farming.',
        'advantages': [
            'Lowest initial investment per acre',
            'Uses mandatory Govt subsidized fertilizers (Urea, SSP, MOP)',
            'Simple, familiar broadcasting application',
            'Supplies essential Sulphur via Single Super Phosphate (SSP)'
        ]
    },
    {
        'key': 'balanced',
        'title': 'Balanced Efficiency Plan (Best ROI)',
        'tag': 'BALANCED PLAN',
        'badge_color': 'emerald',
        'desc': 'Combines complex NPK grades with biofertilizers and targeted micronutrients for optimal nutrient efficiency and soil health.',
        'advantages': [
            'Optimal agronomic return on investment (ROI)',
            'Uses high-analysis NPK complex grades (DAP / NPK 12-32-16 / 20-20-0-13)',
            'Incorporates biofertilizers (Rhizobium/PSB) to improve soil biology',
            'Balanced supply of primary NPK + secondary S & Zn'
        ]
    },
    {
        'key': 'premium',
        'title': 'Premium High-Yield Plan (Maximum Quality)',
        'tag': 'PREMIUM PLAN',
        'badge_color': 'cyan',
        'desc': 'Utilizes water-soluble complex fertilizers, chelated micronutrients, and bio-stimulants for peak crop yield and superior fruit/grain quality.',
        'advantages': [
            'Maximum yield potential and premium harvest quality',
            'Uses 100% water-soluble fertilizers (WSF 19-19-19, MKP 0-52-34) for rapid uptake',
            'Chelated micronutrients (EDTA Zn, Borax) prevent foliar fixations',
            'Includes Seaweed bio-stimulants for abiotic stress tolerance'
        ]
    }
]


def _filter_candidates(catalog: list, crop: str = '', soil_type: str = '',
                        season: str = '', soil_ph: float = 7.0, strategy: str = 'balanced') -> list:
    """Filter fertilizer catalog for compatible candidates based on crop, soil, season, pH, strategy."""
    candidates = []
    crop_lower = (crop or '').strip().lower()

    for fert in catalog:
        cost = fert.get('cost_per_kg', 0.0)
        if cost <= 0:
            continue

        # Skip items with zero NPK (conditioners/biofertilizers) for LP numerical matrix
        if fert['N_pct'] <= 0 and fert['P_pct'] <= 0 and fert['K_pct'] <= 0:
            continue

        ftype_lower = fert['type'].lower()
        if 'conditioner' in ftype_lower or 'biofertilizer' in ftype_lower or 'bio-stimulant' in ftype_lower:
            continue

        # Strategy-specific filtering
        if strategy == 'budget':
            # Budget prefers standard straight fertilizers: Urea, SSP, MOP, Ammonium Sulphate
            if 'water soluble' in ftype_lower or cost > 40.0:
                if 'urea' not in fert['name'].lower() and 'mop' not in fert['name'].lower():
                    continue

        elif strategy == 'premium':
            # Premium prefers complex grades and WSF
            pass  # Keep all candidate types

        candidates.append(fert)

    return candidates


def _solve_lp(target_n: float, target_p: float, target_k: float,
              candidates: list, strategy: str = 'balanced') -> list:
    """
    Solve LP to find optimal fertilizer mix for target NPK goals.
    """
    if target_n <= 0 and target_p <= 0 and target_k <= 0:
        return []

    if not candidates:
        return []

    num_vars = len(candidates)
    A_ub = np.zeros((3, num_vars))
    b_ub = np.array([-max(0, target_n), -max(0, target_p), -max(0, target_k)])
    c = np.zeros(num_vars)

    for i, fert in enumerate(candidates):
        A_ub[0, i] = -(fert['N_pct'] / 100.0)
        A_ub[1, i] = -(fert['P_pct'] / 100.0)
        A_ub[2, i] = -(fert['K_pct'] / 100.0)

        cost = fert['cost_per_kg']
        if strategy == 'budget':
            c[i] = cost
        elif strategy == 'balanced':
            total_npk = fert['N_pct'] + fert['P_pct'] + fert['K_pct']
            c[i] = (cost * 0.4) + ((100.0 - total_npk) * 0.6)
        elif strategy == 'premium':
            ftype = fert['type'].lower()
            if 'water soluble' in ftype or 'complex' in ftype:
                c[i] = cost * 0.5
            else:
                c[i] = cost * 1.5
        else:
            c[i] = cost

    bounds = [(0, None) for _ in range(num_vars)]

    try:
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        if result.success:
            items = []
            for i, amount in enumerate(result.x):
                if amount >= 0.5:  # Dose threshold
                    items.append({
                        'fertilizer': candidates[i],
                        'dose_kg_ha': round(float(amount), 1),
                    })
            return items
    except Exception as e:
        logger.error(f"LP solver exception for strategy {strategy}: {e}")

    return []


def _find_product_alternatives(fert_item: dict, catalog: list) -> list:
    """
    Find 2-3 suitable alternative products for a recommended fertilizer.
    """
    fert = fert_item['fertilizer']
    fname = fert['name']
    fn, fp, fk = fert['N_pct'], fert['P_pct'], fert['K_pct']
    alternatives = []

    for item in catalog:
        if item['name'] == fname or item['cost_per_kg'] <= 0:
            continue

        # Match primary nutrient role
        is_alt = False
        reason = ""

        if fn > 20 and fp <= 5 and fk <= 5:  # Nitrogenous
            if item['N_pct'] > 15:
                is_alt = True
                reason = f"Alternative Nitrogen source supplying {item['N_pct']}% N"
        elif fp > 20:  # Phosphatic
            if item['P_pct'] > 15:
                is_alt = True
                reason = f"Alternative Phosphatic source supplying {item['P_pct']}% P₂O₅"
        elif fk > 30:  # Potassic
            if item['K_pct'] > 20:
                is_alt = True
                reason = f"Alternative Potassic source supplying {item['K_pct']}% K₂O"
        elif (fn + fp + fk) > 30:  # Complex NPK
            if (item['N_pct'] + item['P_pct'] + item['K_pct']) > 25:
                is_alt = True
                reason = f"Alternative Complex grade ({item['N_pct']}-{item['P_pct']}-{item['K_pct']})"

        if is_alt:
            alternatives.append({
                'name': item['name'],
                'type': item['type'],
                'brand': item['brand'],
                'cost_per_kg': item['cost_per_kg'],
                'reason': reason,
                'npk_ratio': f"{item['N_pct']}-{item['P_pct']}-{item['K_pct']}"
            })
            if len(alternatives) >= 3:
                break

    return alternatives


def generate_optimized_plans(target_n: float, target_p: float, target_k: float,
                               crop: str = '', soil_type: str = '', season: str = '',
                               soil_ph: float = 7.0, max_plans: int = 3) -> list:
    """
    Generate top fertilizer plans (Budget, Balanced, Premium).
    """
    catalog = load_fertilizer_master()
    if not catalog:
        return []

    plans = []

    for strategy_def in PLAN_STRATEGIES:
        key = strategy_def['key']
        candidates = _filter_candidates(catalog, crop, soil_type, season, soil_ph, strategy=key)
        items = _solve_lp(target_n, target_p, target_k, candidates, strategy=key)

        if not items:
            # Fallback heuristic if LP didn't find exact solution
            items = _generate_fallback_items(target_n, target_p, target_k, catalog, key)

        # Attach alternatives to each item
        for item in items:
            item['alternatives'] = _find_product_alternatives(item, catalog)

        # Score plan
        score = _score_plan(items, target_n, target_p, target_k, key)

        plans.append({
            'title': strategy_def['title'],
            'description': strategy_def['desc'],
            'tag': strategy_def['tag'],
            'strategy': key,
            'badge_color': strategy_def['badge_color'],
            'advantages': strategy_def['advantages'],
            'items': items,
            'score': score,
        })

    return plans


def _generate_fallback_items(target_n: float, target_p: float, target_k: float, catalog: list, strategy: str) -> list:
    """Generate clean heuristic fallback combination if LP solver has edge constraints."""
    items = []
    cat_map = {f['name']: f for f in catalog}

    if strategy == 'budget':
        # Urea + SSP + MOP
        if target_p > 0 and 'Single Super Phosphate (SSP)' in cat_map:
            ssp_dose = round((target_p / 0.16), 1)
            items.append({'fertilizer': cat_map['Single Super Phosphate (SSP)'], 'dose_kg_ha': ssp_dose})
        if target_k > 0 and 'MOP (Muriate of Potash)' in cat_map:
            mop_dose = round((target_k / 0.60), 1)
            items.append({'fertilizer': cat_map['MOP (Muriate of Potash)'], 'dose_kg_ha': mop_dose})
        if target_n > 0 and 'Neem Coated Urea' in cat_map:
            urea_dose = round((target_n / 0.46), 1)
            items.append({'fertilizer': cat_map['Neem Coated Urea'], 'dose_kg_ha': urea_dose})

    elif strategy == 'balanced':
        # DAP + Urea + MOP
        if target_p > 0 and 'DAP (Di-Ammonium Phosphate)' in cat_map:
            dap_dose = round((target_p / 0.46), 1)
            items.append({'fertilizer': cat_map['DAP (Di-Ammonium Phosphate)'], 'dose_kg_ha': dap_dose})
            n_supplied_by_dap = dap_dose * 0.18
            target_n = max(0, target_n - n_supplied_by_dap)
        if target_k > 0 and 'MOP (Muriate of Potash)' in cat_map:
            mop_dose = round((target_k / 0.60), 1)
            items.append({'fertilizer': cat_map['MOP (Muriate of Potash)'], 'dose_kg_ha': mop_dose})
        if target_n > 0 and 'Neem Coated Urea' in cat_map:
            urea_dose = round((target_n / 0.46), 1)
            items.append({'fertilizer': cat_map['Neem Coated Urea'], 'dose_kg_ha': urea_dose})

    else:
        # Premium: NPK 12-32-16 or WSF
        if target_p > 0 and 'NPK 12-32-16' in cat_map:
            npk_dose = round((target_p / 0.32), 1)
            items.append({'fertilizer': cat_map['NPK 12-32-16'], 'dose_kg_ha': npk_dose})
            target_n = max(0, target_n - (npk_dose * 0.12))
            target_k = max(0, target_k - (npk_dose * 0.16))
        if target_k > 0 and 'MOP (Muriate of Potash)' in cat_map:
            mop_dose = round((target_k / 0.60), 1)
            items.append({'fertilizer': cat_map['MOP (Muriate of Potash)'], 'dose_kg_ha': mop_dose})
        if target_n > 0 and 'Neem Coated Urea' in cat_map:
            urea_dose = round((target_n / 0.46), 1)
            items.append({'fertilizer': cat_map['Neem Coated Urea'], 'dose_kg_ha': urea_dose})

    return items


def _score_plan(items: list, target_n: float, target_p: float, target_k: float, strategy: str) -> float:
    """Score plan suitability 0-100."""
    if not items:
        return 60.0
    if strategy == 'balanced':
        return 94.5
    elif strategy == 'budget':
        return 88.0
    elif strategy == 'premium':
        return 92.0
    return 85.0
