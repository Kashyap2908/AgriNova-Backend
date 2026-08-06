"""
Cost & Bag Calculator Engine
Calculates dosage per acre, total farm quantity, dynamic bag count (45kg for Urea, 50kg others), total estimated cost, and cost per acre.
"""

import math
import logging

logger = logging.getLogger(__name__)


class CostCalculator:
    """
    Computes precise quantity, bag count, total cost, and cost per acre for fertilizer recommendation items.
    """

    @staticmethod
    def calculate_solution_cost(items: list, area: float = 1.0, farm_area_acres: float = None) -> dict:
        """
        Dynamically calculates solution cost by iterating over items.
        items: list of dicts, e.g. [{'fertilizer': {...}, 'dose_kg_ha': float}]
        area / farm_area_acres: farm area in acres.
        Bag size: 45kg if 'urea' in fert['name'].lower(), else 50kg.
        """
        if farm_area_acres is None:
            farm_area_acres = area
        farm_area_acres = max(0.1, float(farm_area_acres or 1.0))

        # Conversion: 1 Hectare = 2.47105 Acres
        ha_to_acre = 1.0 / 2.47105

        processed_items = []
        total_solution_cost = 0.0

        for item in (items or []):
            if not isinstance(item, dict):
                continue

            # Extract fertilizer catalog dict and dose_kg_ha
            if 'fertilizer' in item and isinstance(item['fertilizer'], dict):
                fert = item['fertilizer']
                dose_kg_ha = float(item.get('dose_kg_ha', 0.0) or 0.0)
            else:
                fert = item
                dose_kg_ha = float(item.get('dose_kg_ha', (item.get('dose_per_acre_kg', 0.0) or 0.0) * 2.47105) or 0.0)

            fert_name = fert.get('name') or fert.get('fertilizer_name') or 'Fertilizer'
            fert_type = fert.get('type', '')
            price_per_kg = float(fert.get('price', 0.0) or 0.0)
            app_method = fert.get('application_method', '')

            # Dose per acre
            dose_kg_acre = round(dose_kg_ha * ha_to_acre, 1)

            # Total quantity for farm area
            total_qty_kg = round(dose_kg_acre * farm_area_acres, 1)

            # Bag size check: 45kg if 'urea' in fert['name'].lower(), else 50kg
            bag_size = 45.0 if 'urea' in fert_name.lower() else 50.0
            bags_count = math.ceil(total_qty_kg / bag_size) if total_qty_kg > 0 else 0

            # Item total cost
            item_cost = round(total_qty_kg * price_per_kg, 2)
            total_solution_cost += item_cost

            processed_items.append({
                'fertilizer_name': fert_name,
                'type': fert_type,
                'dose_per_acre_kg': dose_kg_acre,
                'dose_kg_ha': round(dose_kg_ha, 1),
                'total_quantity_kg': total_qty_kg,
                'bag_size_kg': bag_size,
                'total_bags': bags_count,
                'price_per_kg': price_per_kg,
                'item_cost_inr': item_cost,
                'application_method': app_method
            })

        cost_per_acre = round(total_solution_cost / farm_area_acres, 2)

        return {
            'items': processed_items,
            'total_cost_inr': round(total_solution_cost, 2),
            'cost_per_acre_inr': cost_per_acre,
            'farm_area_acres': farm_area_acres
        }


def calculate_solution_cost(items: list, area: float = 1.0, farm_area_acres: float = None) -> dict:
    return CostCalculator.calculate_solution_cost(items, area=area, farm_area_acres=farm_area_acres)

