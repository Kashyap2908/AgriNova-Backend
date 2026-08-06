"""
Agronomic Rule Engine
Applies professional agricultural rules for soil pH amendments, texture split dosage, and nutrient deficiency flags.
Returns validation strings and warnings without selecting fertilizers.
"""

import logging

logger = logging.getLogger(__name__)


class AgronomicRuleEngine:
    """
    Applies expert agricultural rules for soil management, pH amendments, and split application advice.
    ONLY returns validation strings and warnings. Does NOT select or score fertilizers.
    """

    @staticmethod
    def get_rules(deficiency_n: float = 0.0, deficiency_p: float = 0.0, deficiency_k: float = 0.0,
                  soil_ph: float = 7.0, soil_type: str = '', rainfall_mm: float = 0.0) -> dict:
        """
        Evaluates agronomic rules and returns validation strings, warnings, amendments, and precautions.
        Completely free of any fertilizer selection logic.
        """
        rules_applied = []
        amendments = []
        precautions = []
        warnings = []

        # 1. Soil pH Rules & Amendments
        if soil_ph < 6.0:
            warnings.append(f"Acidic soil detected (pH {soil_ph}), apply lime")
            amendments.append({
                'amendment': 'Agricultural Lime (Calcium Carbonate)',
                'reason': f'Acidic soil detected (pH {soil_ph}), apply lime to neutralize soil acidity and unlock fixed Phosphorus.',
                'dose_kg_ha': 250.0
            })
            rules_applied.append('Acidic Soil Amendment (Lime) Applied')
        elif soil_ph > 8.2:
            warnings.append(f"High pH detected (pH {soil_ph}), apply gypsum")
            amendments.append({
                'amendment': 'Gypsum (Calcium Sulphate) / Elemental Sulphur',
                'reason': f'High pH detected (pH {soil_ph}), apply gypsum to reduce sodicity and improve nutrient bioavailability.',
                'dose_kg_ha': 300.0
            })
            rules_applied.append('Alkaline Soil Amendment (Gypsum) Applied')

        # 2. Soil Texture Specific Rules
        soil_clean = (soil_type or '').strip().lower()
        if 'sandy' in soil_clean:
            precautions.append('Sandy soil detected: Divide Nitrogen doses into 3-4 smaller split applications to prevent rapid leaching.')
            rules_applied.append('Sandy Soil Leaching Prevention Rule')
        elif 'clay' in soil_clean:
            precautions.append('Clay soil detected: Incorporate basal fertilizer deeply during tillage for optimum root zone uptake.')
            rules_applied.append('Clay Soil Deep Incorporation Rule')

        # 3. Weather Rainfall Rules
        if rainfall_mm > 20.0:
            precautions.append(f'High rainfall predicted ({rainfall_mm} mm): Defer top-dressing broadcast until rain stops to avoid surface runoff losses.')
            rules_applied.append('Rainfall Runoff Prevention Rule')

        # 4. Standard Agronomic Safety & Handling Precautions
        precautions.append('Apply top-dressing Nitrogen during early morning or late evening, followed by light irrigation to maximize root absorption.')
        precautions.append('Keep concentrated basal fertilizer granules 3-5 cm away from seeds during sowing to prevent germination burn.')
        precautions.append('Store fertilizers in cool, dry, moisture-proof storage away from direct sunlight and livestock.')

        # 5. Nutrient Deficiency Flags
        if deficiency_n > 50.0:
            rules_applied.append('High Nitrogen Deficiency Flagged')
        if deficiency_p > 30.0:
            rules_applied.append('High Phosphorus Deficiency Flagged')
        if deficiency_k > 30.0:
            rules_applied.append('High Potassium Deficiency Flagged')

        return {
            'rules_applied': rules_applied,
            'amendments': amendments,
            'precautions': precautions,
            'warnings': warnings
        }

    @staticmethod
    def evaluate_rules(deficiency_n: float = 0.0, deficiency_p: float = 0.0, deficiency_k: float = 0.0,
                       soil_ph: float = 7.0, soil_type: str = '', rainfall_mm: float = 0.0) -> dict:
        return AgronomicRuleEngine.get_rules(
            deficiency_n=deficiency_n,
            deficiency_p=deficiency_p,
            deficiency_k=deficiency_k,
            soil_ph=soil_ph,
            soil_type=soil_type,
            rainfall_mm=rainfall_mm
        )

