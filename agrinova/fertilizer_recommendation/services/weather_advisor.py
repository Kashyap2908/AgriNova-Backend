"""
Weather Advisor — Integrates with WeatherCacheService to generate weather-based advisories.
"""

import logging

logger = logging.getLogger(__name__)


def get_weather_for_farm(farm_id: int) -> dict:
    """
    Fetch weather data for a farm using WeatherCacheService.
    Returns weather dict or empty dict on failure.
    """
    try:
        from weather.services import WeatherCacheService
        return WeatherCacheService.get_weather_data(farm_id)
    except Exception as e:
        logger.warning(f"Could not fetch weather for farm {farm_id}: {e}")
        return {}


def generate_weather_advisory(weather_data: dict) -> dict:
    """
    Generate agronomic advisory based on current and forecast weather.
    """
    if not weather_data:
        return {
            'status': 'unavailable',
            'advisories': [
                {
                    'type': 'info',
                    'icon': 'sun',
                    'title': 'Standard Application Conditions',
                    'message': 'Weather cache unavailable. Follow standard agronomic practices: apply fertilizers under optimal soil moisture and avoid spraying during hot peak sun hours.'
                }
            ],
            'current_summary': 'Weather baseline active (standard local conditions).'
        }

    current = weather_data.get('current_weather', {})
    daily = weather_data.get('daily_forecast', [])

    if not current or current.get('error'):
        return {
            'status': 'unavailable',
            'advisories': [
                {
                    'type': 'info',
                    'icon': 'sun',
                    'title': 'Standard Application Guidelines',
                    'message': 'Apply fertilizers when soil has adequate moisture. Avoid foliar spraying during high winds or heavy rain.'
                }
            ],
            'current_summary': 'Weather baseline active.'
        }

    temp = float(current.get('temperature', 28) or 28)
    humidity = float(current.get('humidity', 65) or 65)
    rainfall = float(current.get('rainfall', 0) or 0)
    wind = float(current.get('wind_speed', 5) or 5)

    advisories = []

    # 1. Temperature Advisories
    if temp > 38:
        advisories.append({
            'type': 'warning',
            'icon': 'thermometer',
            'title': 'Extreme Heat Warning (>38°C)',
            'message': f'Current temperature is {temp}°C. Do NOT apply foliar sprays or broadcast urea during peak daytime hours (10 AM – 4 PM). High heat accelerates ammonia volatilization. Apply fertilizers late evening after 4 PM.'
        })
    elif temp > 35:
        advisories.append({
            'type': 'caution',
            'icon': 'thermometer',
            'title': 'High Temperature Alert (35-38°C)',
            'message': f'Temperature is {temp}°C. Recommend evening fertilizer application to maximize nutrient absorption and prevent leaf burn.'
        })

    # 2. Humidity Advisories (Fungal Risk)
    if humidity > 80:
        advisories.append({
            'type': 'warning',
            'icon': 'droplets',
            'title': 'High Humidity Alert (>80%)',
            'message': f'Relative humidity is {humidity}%. High moisture accelerates fungal spore germination (Tikka/Blast/Blight/Rust). Preventive fungicide application is strongly advised.'
        })

    # 3. Heavy Rain Forecast Advisories
    if rainfall > 15:
        advisories.append({
            'type': 'warning',
            'icon': 'cloud-rain',
            'title': 'Heavy Rain Forecast (>15 mm)',
            'message': f'Rainfall is {rainfall} mm. Postpone granular fertilizer broadcasting by 2-3 days to prevent heavy Nitrogen leaching loss into groundwater.'
        })
    elif rainfall > 5:
        advisories.append({
            'type': 'info',
            'icon': 'cloud-rain',
            'title': 'Favorable Moisture Conditions',
            'message': f'Light/Moderate rain of {rainfall} mm provides ideal soil moisture for basal fertilizer absorption.'
        })

    # 4. Wind Speed Advisories
    if wind > 20:
        advisories.append({
            'type': 'caution',
            'icon': 'wind',
            'title': 'High Wind Warning (>20 km/h)',
            'message': f'Wind speed is {wind} km/h. Avoid foliar chemical spraying and fine granular broadcasting due to heavy wind drift.'
        })

    summary = f"Currently {temp}°C with {humidity}% humidity, {rainfall} mm rain, wind {wind} km/h."

    return {
        'status': 'available',
        'current_summary': summary,
        'temperature': temp,
        'humidity': humidity,
        'rainfall': rainfall,
        'wind_speed': wind,
        'advisories': advisories,
    }
