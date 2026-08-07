"""
Cost Engine — Comprehensive itemized cost calculator for fertilizer & crop protection plans.
Computes itemized and category-wise costs in ₹, preserving farmer's area unit.
"""

import logging
from .area_converter import to_hectares, format_quantity

logger = logging.getLogger(__name__)


def calculate_plan_cost(plan_items: list, farm_area: float, area_unit: str) -> dict:
    """
    Calculate itemized and total cost for a fertilizer plan.
    plan_items: list of {'fertilizer': dict, 'dose_kg_ha': float}
    Returns: {'items': [...], 'total_cost': float, 'cost_per_unit': float}
    """
    area_ha = to_hectares(farm_area, area_unit)
    items_costed = []
    total_cost = 0.0

    for item in plan_items:
        fert = item['fertilizer']
        dose_per_ha = item['dose_kg_ha']
        total_kg = round(dose_per_ha * area_ha, 1)
        cost_per_kg = fert.get('cost_per_kg', 0.0)
        item_cost = round(total_kg * cost_per_kg, 2)
        total_cost += item_cost

        qty_info = format_quantity(total_kg, farm_area, area_unit)

        items_costed.append({
            'name': fert['name'],
            'type': fert['type'],
            'brand': fert.get('brand', 'Standard'),
            'dose_per_ha': dose_per_ha,
            'total_quantity_kg': total_kg,
            'quantity_display': qty_info,
            'cost_per_kg': cost_per_kg,
            'bag_size': fert.get('Bag_Size_Kg', 50),
            'price_per_bag': fert.get('Price_Per_Bag_INR', round(cost_per_kg * 50, 0)),
            'item_cost': item_cost,
            'cost_display': f"₹{item_cost:,.0f}",
            'unit': fert.get('unit', 'kg'),
            'npk_ratio': f"{fert.get('N_pct', 0)}-{fert.get('P_pct', 0)}-{fert.get('K_pct', 0)}",
            'application_method': fert.get('application_method', 'Broadcasting'),
            'alternatives': item.get('alternatives', []),
        })

    cost_per_unit = round(total_cost / farm_area, 2) if farm_area > 0 else 0.0

    return {
        'items': items_costed,
        'total_cost': round(total_cost, 2),
        'total_cost_display': f"₹{total_cost:,.0f}",
        'cost_per_unit': cost_per_unit,
        'cost_per_unit_display': f"₹{cost_per_unit:,.0f} per {area_unit}",
        'area_display': f"{farm_area} {area_unit}",
    }


def calculate_protection_cost(protection_plan: dict, farm_area: float, area_unit: str) -> dict:
    """
    Calculate itemized protection costs: Herbicide, Fungicide, Insecticide, Micronutrient, Growth Regulator.
    """
    area_ha = to_hectares(farm_area, area_unit)
    acres = area_ha / 0.4047

    herbicide_cost = 0.0
    fungicide_cost = 0.0
    insecticide_cost = 0.0
    micronutrient_cost = 0.0
    growth_regulator_cost = 0.0

    for item in protection_plan.get('weed_management', []):
        herbicide_cost += item.get('estimated_cost_per_acre', 0.0) * acres

    for item in protection_plan.get('disease_prevention', []):
        fungicide_cost += item.get('estimated_cost_per_acre', 0.0) * acres

    for item in protection_plan.get('pest_management', []):
        insecticide_cost += item.get('estimated_cost_per_acre', 0.0) * acres

    for item in protection_plan.get('micronutrient_spray', []):
        micronutrient_cost += item.get('estimated_cost_per_acre', 0.0) * acres

    for item in protection_plan.get('growth_promoter', []):
        growth_regulator_cost += item.get('estimated_cost_per_acre', 0.0) * acres

    total_protection = herbicide_cost + fungicide_cost + insecticide_cost + micronutrient_cost + growth_regulator_cost

    return {
        'herbicide_cost': round(herbicide_cost, 2),
        'herbicide_cost_display': f"₹{herbicide_cost:,.0f}",
        'fungicide_cost': round(fungicide_cost, 2),
        'fungicide_cost_display': f"₹{fungicide_cost:,.0f}",
        'insecticide_cost': round(insecticide_cost, 2),
        'insecticide_cost_display': f"₹{insecticide_cost:,.0f}",
        'micronutrient_cost': round(micronutrient_cost, 2),
        'micronutrient_cost_display': f"₹{micronutrient_cost:,.0f}",
        'growth_regulator_cost': round(growth_regulator_cost, 2),
        'growth_regulator_cost_display': f"₹{growth_regulator_cost:,.0f}",
        'total_protection_cost': round(total_protection, 2),
        'total_protection_cost_display': f"₹{total_protection:,.0f}",
        'per_acre': round(total_protection / acres, 2) if acres > 0 else 0.0,
    }


def calculate_grand_total(nutrition_cost: dict, protection_cost: dict, farm_area: float = 1.0, area_unit: str = 'Acres') -> dict:
    """
    Compute full itemized cost summary:
    - Fertilizer Cost
    - Micronutrient Cost
    - Herbicide Cost
    - Fungicide Cost
    - Insecticide Cost
    - Growth Regulator Cost
    - Application / Labour Cost (estimated @ ₹400/acre for spraying & broadcasting)
    - Miscellaneous Cost (Seed treatment / biofertilizer inoculants)
    - Total Nutrition Cost
    - Total Protection Cost
    - Grand Total Cost
    """
    area_ha = to_hectares(farm_area, area_unit)
    acres = area_ha / 0.4047

    fert_cost = nutrition_cost.get('total_cost', 0.0)
    micro_cost = protection_cost.get('micronutrient_cost', 0.0)
    herb_cost = protection_cost.get('herbicide_cost', 0.0)
    fung_cost = protection_cost.get('fungicide_cost', 0.0)
    insec_cost = protection_cost.get('insecticide_cost', 0.0)
    pgr_cost = protection_cost.get('growth_regulator_cost', 0.0)

    # Optional / reasonable estimates for application & biofertilizer inoculants
    application_cost = round(acres * 350.0, 2)  # ~₹350/acre application labour
    misc_cost = round(acres * 150.0, 2)         # ~₹150/acre inoculants/stickers

    total_nutrition = fert_cost + micro_cost + misc_cost
    total_protection = herb_cost + fung_cost + insec_cost + pgr_cost
    grand_total = total_nutrition + total_protection + application_cost

    return {
        'fertilizer_cost': fert_cost,
        'fertilizer_cost_display': f"₹{fert_cost:,.0f}",
        'micronutrient_cost': micro_cost,
        'micronutrient_cost_display': f"₹{micro_cost:,.0f}",
        'herbicide_cost': herb_cost,
        'herbicide_cost_display': f"₹{herb_cost:,.0f}",
        'fungicide_cost': fung_cost,
        'fungicide_cost_display': f"₹{fung_cost:,.0f}",
        'insecticide_cost': insec_cost,
        'insecticide_cost_display': f"₹{insec_cost:,.0f}",
        'growth_regulator_cost': pgr_cost,
        'growth_regulator_cost_display': f"₹{pgr_cost:,.0f}",
        'application_cost': application_cost,
        'application_cost_display': f"₹{application_cost:,.0f}",
        'miscellaneous_cost': misc_cost,
        'miscellaneous_cost_display': f"₹{misc_cost:,.0f}",
        'total_nutrition_cost': round(total_nutrition, 2),
        'total_nutrition_cost_display': f"₹{total_nutrition:,.0f}",
        'total_protection_cost': round(total_protection, 2),
        'total_protection_cost_display': f"₹{total_protection:,.0f}",
        'grand_total': round(grand_total, 2),
        'grand_total_display': f"₹{grand_total:,.0f}",
    }
