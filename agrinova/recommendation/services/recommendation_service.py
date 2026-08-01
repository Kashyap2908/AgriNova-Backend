from farms.models import Farm
from recommendation.weather.weather_service import fetch_current_weather
from recommendation.season.season_service import determine_season
from recommendation.builders.feature_builder import build_feature_dictionary
from recommendation.engine.recommendation_engine import generate_recommendation
from recommendation.models import RecommendationHistory
from django.core.exceptions import ObjectDoesNotExist

def generate_crop_recommendation(user, farm_id: int) -> dict:
    """
    Orchestrates the crop recommendation flow.
    Views must call this service rather than containing business logic.
    """
    try:
        farm = Farm.objects.get(id=farm_id, user=user)
    except ObjectDoesNotExist:
        raise ValueError("Farm not found or does not belong to the user.")

    # 1. Load Weather
    weather_data = fetch_current_weather(farm.latitude, farm.longitude)

    # 2. Determine Season
    season = determine_season()

    # 3. Build Feature Dictionary
    feature_dict = build_feature_dictionary(farm, weather_data, season)

    # 4. Call Recommendation Engine
    engine_result = generate_recommendation(feature_dict)

    # 5. Save Recommendation History
    history = RecommendationHistory.objects.create(
        user=user,
        farm=farm,
        recommended_crop=engine_result.get('recommended_crop'),
        confidence=engine_result.get('confidence'),
        season=season,
        weather_snapshot=weather_data,
        feature_snapshot=feature_dict,
        prediction_source=engine_result.get('prediction_source', 'Dummy')
    )

    # 6. Return Response mapped to API requirements
    return {
        "recommendation": {
            "crop": history.recommended_crop,
            "confidence": history.confidence,
            "prediction_source": history.prediction_source,
            "reason": engine_result.get('reason', [])
        },
        "farm": {
            "id": farm.id,
            "name": farm.farm_name,
            "location": f"{farm.village}, {farm.district}, {farm.state}",
            "nitrogen": farm.nitrogen,
            "phosphorus": farm.phosphorus,
            "potassium": farm.potassium,
            "soil_ph": farm.soil_ph
        },
        "weather": weather_data,
        "season": season
    }
