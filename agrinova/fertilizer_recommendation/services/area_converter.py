"""
Area Converter — Handles conversion between Indian land measurement units.
Preserves farmer's original unit and converts internally to hectares for calculations.
"""

import logging

logger = logging.getLogger(__name__)

# Conversion factors to hectares
UNIT_TO_HECTARE = {
    'hectare': 1.0,
    'hectares': 1.0,
    'ha': 1.0,
    'acre': 0.4047,
    'acres': 0.4047,
    'bigha': 0.2529,    # Standard bigha (UP/Bihar standard)
    'bighas': 0.2529,
    'guntha': 0.01012,  # 1 guntha = 1/40 acre
    'gunthas': 0.01012,
    'cent': 0.004047,   # 100 cents = 1 acre
    'cents': 0.004047,
    'kanal': 0.0505,    # 1 kanal = 1/8 acre (Punjab/Haryana)
    'kanals': 0.0505,
    'marla': 0.00253,
    'marlas': 0.00253,
    'sq_ft': 0.0000929,
    'sq_m': 0.0001,
}


def to_hectares(area: float, unit: str) -> float:
    """Convert any supported area unit to hectares."""
    unit_key = (unit or 'acres').strip().lower()
    factor = UNIT_TO_HECTARE.get(unit_key, 0.4047)  # Default to acres
    return max(0.01, round(float(area or 1.0) * factor, 4))


def from_hectares(area_ha: float, unit: str) -> float:
    """Convert hectares back to the farmer's original unit."""
    unit_key = (unit or 'acres').strip().lower()
    factor = UNIT_TO_HECTARE.get(unit_key, 0.4047)
    if factor <= 0:
        factor = 0.4047
    return round(area_ha / factor, 2)


def format_quantity(qty_kg: float, farm_area: float, area_unit: str) -> dict:
    """Format quantity display using farmer's original area unit."""
    unit_clean = (area_unit or 'Acres').strip()
    area_ha = to_hectares(farm_area, unit_clean)
    qty_per_ha = qty_kg / area_ha if area_ha > 0 else qty_kg
    qty_per_unit = qty_kg / farm_area if farm_area > 0 else qty_kg

    # Estimate bag count (assuming 50kg standard bag or 45kg urea bag)
    bags = round(qty_kg / 50.0, 1)
    bags_text = f"{bags} bags" if bags >= 1 else f"{round(qty_kg, 1)} kg"

    return {
        'total_kg': round(qty_kg, 1),
        'per_hectare_kg': round(qty_per_ha, 1),
        'per_unit_kg': round(qty_per_unit, 1),
        'per_unit_text': f"{round(qty_per_unit, 1)} kg per {unit_clean}",
        'total_text': f"{round(qty_kg, 1)} kg ({bags_text}) for {farm_area} {unit_clean}",
        'bags': bags,
    }
