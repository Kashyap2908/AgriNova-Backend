def build_feature_dictionary(farm, weather_data: dict, season: str) -> dict:
    """
    Builds the complete feature dictionary required by the recommendation engine (and future ML model).
    """
    return {
        "nitrogen": farm.nitrogen,
        "phosphorus": farm.phosphorus,
        "potassium": farm.potassium,
        "soil_ph": farm.soil_ph,
        
        "temperature": weather_data.get("temperature"),
        "humidity": weather_data.get("humidity"),
        "rainfall": weather_data.get("rainfall"),
        
        "season": season,
        
        "soil_type": farm.soil_type,
        "water_availability": farm.water_availability,
        "irrigation_type": farm.irrigation_type,
        "farm_area": float(farm.farm_area) if farm.farm_area else None,
        "latitude": farm.latitude,
        "longitude": farm.longitude
    }
