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
    farms = Farm.objects.filter(user=user)
    
    if not farms.exists():
        logger.warning(f"No farms found for user {user.username}")
    
    for farm in farms:
        logger.info(f"Processing farm: {farm.name}")
        
        # 1. Weather Notifications
        try:
            weather = WeatherCache.objects.get(farm=farm)
            logger.info(f"Weather data found for {farm.name}")
            if weather.current_weather:
                temp = weather.current_weather.get('temp_c', 0)
                precip = weather.current_weather.get('precip_mm', 0)
                condition = weather.current_weather.get('condition', {}).get('text', '').lower()
                wind = weather.current_weather.get('wind_kph', 0)
                
                logger.info(f"Weather checks -> Temp: {temp}, Precip: {precip}, Cond: {condition}, Wind: {wind}")

                if 'rain' in condition or precip > 5:
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
                if 'storm' in condition or 'thunder' in condition:
                    count += create_notification(user, farm, "Storm Warning", "Thunderstorm expected.", "weather", "storm")
        except WeatherCache.DoesNotExist:
            logger.warning(f"No weather cache found for {farm.name}")

        # 2. Market Notifications
        latest_market = MarketForecastHistory.objects.filter(farm=farm).order_by('-created_at').first()
        if latest_market:
            logger.info(f"Market data found for {farm.name} (Crop: {latest_market.crop}, Trend: {latest_market.trend})")
            if latest_market.trend == 'up':
                count += create_notification(user, farm, "Market Price Update", f"{latest_market.crop.capitalize()} prices have increased.", "market", f"market_up_{latest_market.crop}")
            elif latest_market.trend == 'down':
                count += create_notification(user, farm, "Market Price Alert", f"{latest_market.crop.capitalize()} prices trending downwards.", "market", f"market_down_{latest_market.crop}")
        else:
            logger.info(f"No market data found for {farm.name}")

        # 3. Crop Recommendation Notifications
        latest_crop = RecommendationHistory.objects.filter(farm=farm).order_by('-created_at').first()
        if latest_crop:
            days_diff = (timezone.now() - latest_crop.created_at).days
            logger.info(f"Crop rec found for {farm.name}, created {days_diff} days ago")
            if days_diff <= 3:
                count += create_notification(user, farm, "New Crop Recommendation", f"A new recommendation is available.", "crop", f"crop_rec_{latest_crop.id}")
        else:
            logger.info(f"No crop data found for {farm.name}")
                
        # 4. Disease Risk Notifications
        try:
            weather = WeatherCache.objects.get(farm=farm)
            if weather.current_weather:
                temp = weather.current_weather.get('temp_c', 0)
                humidity = weather.current_weather.get('humidity', 0)
                logger.info(f"Disease checks -> Temp: {temp}, Humidity: {humidity}")
                if temp > 25 and humidity > 80:
                    count += create_notification(user, farm, "Disease Risk Advisory", "High humidity/temp may increase fungal risk.", "disease", "fungal_risk")
        except WeatherCache.DoesNotExist:
            pass

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
