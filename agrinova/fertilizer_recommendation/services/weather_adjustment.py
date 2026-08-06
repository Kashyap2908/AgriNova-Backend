"""
Weather Intelligence Adjustment Engine
Integrates live weather metrics (rainfall, temp, humidity) to adjust fertilizer dosage timing and split schedule.
Only changes application timing / split logic. Does NOT alter fertilizer types.
"""

import logging

logger = logging.getLogger(__name__)


class WeatherAdjustmentEngine:
    """
    Evaluates weather parameters to refine fertilizer application timing and split logic.
    Does NOT alter fertilizer types.
    """

    @staticmethod
    def get_adjustment(weather: dict = None, **kwargs) -> dict:
        """
        Evaluates weather parameters and returns timing / split logic adjustments.
        e.g. 'Heavy Rain -> Split Nitrogen'
        """
        if weather is None:
            weather = {}
        if isinstance(weather, dict):
            farm_id = weather.get('farm_id') or kwargs.get('farm_id')
            rainfall_mm = float(weather.get('rainfall_mm', weather.get('precip_mm', kwargs.get('rainfall_mm', 0.0))) or 0.0)
            temperature_c = float(weather.get('temperature_c', weather.get('temp_c', kwargs.get('temperature_c', 28.0))) or 28.0)
            humidity_pct = float(weather.get('humidity_pct', kwargs.get('humidity_pct', 65.0)) or 65.0)
        else:
            farm_id = getattr(weather, 'farm_id', kwargs.get('farm_id'))
            rainfall_mm = float(getattr(weather, 'rainfall_mm', kwargs.get('rainfall_mm', 0.0)) or 0.0)
            temperature_c = float(getattr(weather, 'temperature_c', kwargs.get('temperature_c', 28.0)) or 28.0)
            humidity_pct = float(getattr(weather, 'humidity_pct', kwargs.get('humidity_pct', 65.0)) or 65.0)

        # Try fetching real weather from WeatherCacheService if farm_id is provided
        if farm_id:
            try:
                from weather.services import WeatherCacheService
                w_data = WeatherCacheService.get_weather_data(farm_id)
                curr = w_data.get('current', {})
                temperature_c = float(curr.get('temp_c', temperature_c) or temperature_c)
                humidity_pct = float(curr.get('humidity_pct', humidity_pct) or humidity_pct)
                rainfall_mm = float(curr.get('precip_mm', rainfall_mm) or rainfall_mm)
            except Exception as e:
                logger.warning(f"Could not load weather for farm {farm_id}: {e}")

        advices = []
        basal_n_modifier = 1.0  # Default multiplier for timing/split

        # 1. Rainfall Adjustments & Timing Directives (Heavy Rain -> Split Nitrogen)
        if rainfall_mm > 25.0:
            basal_n_modifier = 0.75  # Reduce basal N share and shift to top-dressing
            advices.append(f"Heavy Rain -> Split Nitrogen: High rainfall forecast ({rainfall_mm} mm). Reduced basal Nitrogen by 25% to prevent leaching; shift remaining dose to top-dressing after rain stops.")
        elif rainfall_mm > 10.0:
            advices.append(f"Moderate rainfall expected ({rainfall_mm} mm): Good soil moisture for fertilizer incorporation. Apply basal dose before light shower.")
        else:
            advices.append(f"Precipitation level is low ({rainfall_mm} mm): Field irrigation recommended within 24 hours after broadcasting Nitrogen.")

        # 2. Temperature Adjustments & Directives
        if temperature_c > 35.0:
            advices.append(f"High daytime temperature ({temperature_c}°C): Broadcast Nitrogen ONLY during early morning or late evening followed by light irrigation to avoid ammonia volatilization.")
        elif temperature_c < 12.0:
            advices.append(f"Cool temperature ({temperature_c}°C): Crop nutrient uptake rate is slower; avoid excess foliage spraying.")
        else:
            advices.append(f"Ambient temperature ({temperature_c}°C) is in the optimal range (20–32°C) for vigorous plant nutrient uptake.")

        # 3. Humidity Adjustments & Directives
        if humidity_pct > 85.0:
            advices.append(f"High atmospheric humidity ({humidity_pct}%): Ensure granular fertilizers are stored in moisture-proof bags to prevent caking.")
        else:
            advices.append(f"Relative humidity ({humidity_pct}%): Good condition for fertilizer handling and field application.")

        return {
            'temperature_c': round(temperature_c, 1),
            'humidity_pct': round(humidity_pct, 1),
            'rainfall_mm': round(rainfall_mm, 1),
            'basal_n_modifier': basal_n_modifier,
            'weather_advice': advices,
            'timing_adjustment': "Heavy Rain -> Split Nitrogen" if rainfall_mm > 25.0 else "Standard Timing"
        }

    @staticmethod
    def evaluate_weather_impact(farm_id: int = None, rainfall_mm: float = 0.0,
                                temperature_c: float = 28.0, humidity_pct: float = 65.0) -> dict:
        return WeatherAdjustmentEngine.get_adjustment({
            'farm_id': farm_id,
            'rainfall_mm': rainfall_mm,
            'temperature_c': temperature_c,
            'humidity_pct': humidity_pct
        })

