import logging

logger = logging.getLogger(__name__)

class FertilizerRuleEngine:
    """
    Intelligent Agricultural Rule Engine for Fertilizer Application.
    Applies expert agronomy rules to adjust recommendations based on:
    - Weather intelligence (rainfall, wind speed, temperature)
    - Soil pH correction (Acidic Lime vs Alkaline Gypsum)
    - Crop growth stage (Basal, Vegetative, Flowering)
    - Safety and environmental hazards
    """

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
