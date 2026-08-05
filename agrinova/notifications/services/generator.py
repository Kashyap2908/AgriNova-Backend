import hashlib
import logging
from datetime import datetime
from django.utils import timezone
from notifications.models import Notification
from farms.models import Farm
from weather.models import WeatherCache
from market_forecast.models import MarketForecastHistory
from recommendation.models import RecommendationHistory

logger = logging.getLogger(__name__)

def create_notification(user, farm, title, message, notif_type, hash_key):
    today = timezone.now().date().isoformat()
    raw_string = f"{user.id}_{farm.id if farm else 'none'}_{hash_key}_{today}"
    unique_hash = hashlib.md5(raw_string.encode()).hexdigest()
    
    if not Notification.objects.filter(unique_hash=unique_hash).exists():
        Notification.objects.create(
            user=user,
            farm=farm,
            title=title,
            message=message,
            type=notif_type,
            unique_hash=unique_hash
        )
        logger.info(f"Created notification for {user.username}: {title}")
        return True
    logger.info(f"Skipped duplicate notification for {user.username}: {title} (Hash: {unique_hash})")
    return False

def generate_smart_notifications(user):
    logger.info(f"--- Starting smart notification generation for {user.username} ---")
    count = 0
    try:
        farms = Farm.objects.filter(user=user)
        
        if not farms.exists():
            logger.warning(f"No farms found for user {user.username}")
        
        for farm in farms:
            farm_label = getattr(farm, 'farm_name', getattr(farm, 'name', 'Farm'))
            logger.info(f"Processing farm: {farm_label}")
            
            # 1. Weather Notifications
            try:
                weather = WeatherCache.objects.get(farm=farm)
                logger.info(f"Weather data found for {farm_label}")
                if weather.current_weather:
                    cw = weather.current_weather
                    temp = float(cw.get('temperature') or cw.get('temp_c') or 0)
                    precip = float(cw.get('rainfall') or cw.get('precip_mm') or 0)
                    humidity = float(cw.get('humidity') or 0)
                    wind = float(cw.get('wind_speed') or cw.get('wind_kph') or 0)
                    w_code = int(cw.get('weather_code') or 0)
                    
                    logger.info(f"Weather checks -> Temp: {temp}, Precip: {precip}, Wind: {wind}")

                    if precip > 5 or (61 <= w_code <= 67) or (80 <= w_code <= 82) or (95 <= w_code <= 99):
                        count += create_notification(
                            user, farm, 
                            "Heavy Rainfall Expected", 
                            "Heavy rainfall is expected. Avoid irrigation today.", 
                            "weather", "heavy_rain"
                        )
                        count += create_notification(
                            user, farm,
                            "Irrigation Update",
                            "Rain expected. Irrigation is not required today.",
                            "irrigation", "no_irrigation_needed"
                        )
                    elif temp > 35:
                        count += create_notification(
                            user, farm,
                            "High Temperature Alert",
                            f"Temperature is high ({temp}°C). Ensure your crops have adequate water.",
                            "weather", "high_temp"
                        )
                        count += create_notification(
                            user, farm,
                            "Irrigation Recommended",
                            "High temperatures detected. Irrigation is recommended today.",
                            "irrigation", "irrigation_needed"
                        )
                    
                    if wind > 40:
                        count += create_notification(user, farm, "Strong Wind Warning", "Strong winds detected.", "weather", "strong_wind")
                    if 95 <= w_code <= 99:
                        count += create_notification(user, farm, "Storm Warning", "Thunderstorm expected.", "weather", "storm")
            except WeatherCache.DoesNotExist:
                logger.warning(f"No weather cache found for {farm_label}")
            except Exception as w_err:
                logger.error(f"Error checking weather notifications: {w_err}")

            # 2. Market Notifications
            try:
                latest_market = MarketForecastHistory.objects.filter(farm=farm).order_by('-created_at').first()
                if latest_market:
                    trend_val = str(latest_market.trend or '').lower()
                    if 'up' in trend_val:
                        count += create_notification(user, farm, "Market Price Update", f"{latest_market.crop.capitalize()} prices have increased.", "market", f"market_up_{latest_market.crop}")
                    elif 'down' in trend_val:
                        count += create_notification(user, farm, "Market Price Alert", f"{latest_market.crop.capitalize()} prices trending downwards.", "market", f"market_down_{latest_market.crop}")
            except Exception as m_err:
                logger.error(f"Error checking market notifications: {m_err}")

            # 3. Crop Recommendation Notifications
            try:
                latest_crop = RecommendationHistory.objects.filter(farm=farm).order_by('-created_at').first()
                if latest_crop:
                    days_diff = (timezone.now() - latest_crop.created_at).days
                    if days_diff <= 3:
                        count += create_notification(user, farm, "New Crop Recommendation", f"A new recommendation is available.", "crop", f"crop_rec_{latest_crop.id}")
            except Exception as c_err:
                logger.error(f"Error checking crop notifications: {c_err}")
                    
            # 4. Disease Risk Notifications
            try:
                weather = WeatherCache.objects.get(farm=farm)
                if weather.current_weather:
                    cw = weather.current_weather
                    temp = float(cw.get('temperature') or 0)
                    humidity = float(cw.get('humidity') or 0)
                    if temp > 25 and humidity > 80:
                        count += create_notification(user, farm, "Disease Risk Advisory", "High humidity/temp may increase fungal risk.", "disease", "fungal_risk")
            except Exception as d_err:
                pass

    except Exception as e:
        logger.error(f"Error in generate_smart_notifications: {e}")

    logger.info(f"--- Finished smart notification generation. Generated: {count} ---")
    return count

def generate_test_notification(user):
    import uuid
    hash_val = str(uuid.uuid4())
    Notification.objects.create(
        user=user,
        title="Test Notification",
        message="Smart Notifications are working correctly.",
        type="general",
        unique_hash=hash_val
    )
    return 1
