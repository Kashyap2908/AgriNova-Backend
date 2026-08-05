import logging

logger = logging.getLogger(__name__)

# Standard conversion map to convert land area units to Acres for internal calculations
AREA_TO_ACRE_FACTORS = {
    'acre': 1.0,
    'acres': 1.0,
    'hectare': 2.47105,
    'hectares': 2.47105,
    'ha': 2.47105,
    'bigha': 0.40,
    'bighas': 0.40,
    'guntha': 0.025,
    'gunthas': 0.025,
    'gunthe': 0.025,
    'ground': 0.055,
    'grounds': 0.055,
    'kanal': 0.125,
    'kanals': 0.125,
    'marla': 0.00625,
    'marlas': 0.00625,
}

class FertilizerRuleEngine:
    """
    Intelligent Agricultural Rule Engine for Fertilizer Application.
    Applies expert agronomy rules to adjust recommendations based on:
    - Weather intelligence (rainfall, wind speed, temperature)
    - Soil pH correction (Acidic Lime vs Alkaline Gypsum)
    - Crop growth stage (Basal, Vegetative, Flowering)
    - Land area unit preservation (Acre, Hectare, Bigha, Guntha, Ground)
    - Safety and environmental hazards
    """

    @staticmethod
    def convert_area_to_acres(area_val: float, unit: str) -> float:
        """Converts farm area value in farmer's original unit to Acres for internal calculation."""
        try:
            val = float(area_val or 1.0)
        except (ValueError, TypeError):
            val = 1.0

        unit_clean = str(unit or 'Acres').strip().lower()
        factor = AREA_TO_ACRE_FACTORS.get(unit_clean, 1.0)
        return max(0.01, val * factor)

    @staticmethod
    def format_unit_dosage(total_kg: float, farm_area: float, unit: str) -> dict:
        """Formats dosage and total quantity respecting farmer's original unit."""
        try:
            area_num = float(farm_area or 1.0)
        except (ValueError, TypeError):
            area_num = 1.0

        unit_str = str(unit or 'Acres').strip()
        dosage_per_unit = round(total_kg / max(0.01, area_num), 1)

        return {
            "dosage_per_unit": dosage_per_unit,
            "dosage_per_unit_text": f"{dosage_per_unit} kg/{unit_str}",
            "total_quantity_text": f"{round(total_kg, 1)} kg for {area_num} {unit_str}",
            "area_unit": unit_str
        }

    @staticmethod
    def evaluate_weather_rules(weather_data: dict) -> dict:
        """
        Evaluates weather conditions to determine application safety and timing.
        """
        if not weather_data:
            return {
                "safe_to_apply": True,
                "status": "Safe to Apply",
                "weather_advice": "Weather conditions are normal. Proceed with scheduled fertilizer application.",
                "delay_days": 0
            }

        current = weather_data.get("current_weather", {}) or {}
        rainfall = float(current.get("rainfall", 0.0) or 0.0)
        wind_speed = float(current.get("wind_speed", 0.0) or 0.0)
        temp = float(current.get("temperature", 28.0) or 28.0)

        # Check daily forecast for heavy rain
        daily = weather_data.get("daily_forecast", []) or []
        rain_predicted_soon = False
        for day in daily[:2]:
            if float(day.get("rainfall", 0.0) or 0.0) > 10.0 or float(day.get("rain_probability", 0) or 0) > 70:
                rain_predicted_soon = True
                break

        warnings = []
        safe_to_apply = True
        status = "Safe to Apply"
        delay_days = 0
        weather_advice = "Weather conditions are optimal for fertilizer application."

        if rainfall > 5.0 or rain_predicted_soon:
            safe_to_apply = False
            status = "Delay 2 Days (Rain Hazard)"
            delay_days = 2
            weather_advice = "Heavy rainfall detected or expected in next 48 hours. Delay application to prevent fertilizer runoff & nutrient leaching."
            warnings.append("Heavy rain warning: Do not apply granular fertilizer immediately before or during heavy downpours.")

        if wind_speed > 20.0:
            warnings.append(f"High wind warning ({wind_speed} km/h): Avoid foliar sprays or fine dusting to prevent spray drift.")

        if temp > 36.0:
            warnings.append("High temperature warning (>36°C): Apply fertilizers during early morning or late evening to prevent crop scorching and volatilization losses.")

        return {
            "safe_to_apply": safe_to_apply,
            "status": status,
            "weather_advice": weather_advice,
            "delay_days": delay_days,
            "warnings": warnings,
            "temperature": temp,
            "wind_speed": wind_speed,
            "rainfall": rainfall
        }

    @staticmethod
    def generate_safety_warnings(fertilizer_name: str, weather_rules: dict, soil_ph: float = 6.5) -> list:
        """Generates safety and operational warnings for farmers."""
        warnings = []
        
        # Weather warnings
        warnings.extend(weather_rules.get("warnings", []))

        # Product-specific handling warnings
        fn_lower = fertilizer_name.lower()
        if 'urea' in fn_lower:
            warnings.append("Urea Warning: Do not leave Urea uncovered on soil surface. Incorporate into soil or irrigate immediately to avoid ammonia volatilization losses.")
            warnings.append("Do not apply Urea directly in contact with germinating seeds.")
        elif 'dap' in fn_lower or 'ssp' in fn_lower:
            warnings.append("Phosphatic Fertilizer: Apply deep near the root zone (Basal application) for maximum absorption as phosphorus moves slowly in soil.")
        elif 'mop' in fn_lower:
            warnings.append("Potash Handling: Store in dry conditions as MOP is hygroscopic and can form hard lumps under moisture.")
        elif 'lime' in fn_lower:
            warnings.append("Lime Handling: Wear protective gloves and eye mask during lime application to prevent skin & eye irritation.")

        # Universal Safety Instructions
        warnings.append("General Safety: Wear protective gloves and mask when mixing or spraying fertilizers.")
        warnings.append("Storage: Keep fertilizers in a cool, dry place away from direct sunlight, children, and cattle.")

        return warnings

