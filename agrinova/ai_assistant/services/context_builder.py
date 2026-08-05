from farms.models import Farm
from ai_assistant.agents.weather_agent import get_weather_context
from ai_assistant.agents.market_agent import get_market_context
from ai_assistant.agents.crop_agent import get_crop_context
from ai_assistant.agents.disease_agent import get_disease_context

def build_farm_context(user, farm_id=None):
    """
    Orchestrates domain agents to compile all farm intelligence into 
    a structured dictionary for the LLM context.
    """
    context = {}
    
    # 1. User Context
    try:
        profile = user.profile
        context['farmer_profile'] = {
            "name": profile.full_name,
            "preferred_language": profile.preferred_language
        }
    except Exception:
        context['farmer_profile'] = {"name": user.username}
        
    # 2. Farm Context & Agents
    if farm_id:
        try:
            farm = Farm.objects.get(id=farm_id, user=user)
            context['farm_details'] = {
                "name": farm.farm_name,
                "location": f"{farm.village}, {farm.district}, {farm.state}",
                "area": f"{farm.farm_area} {farm.area_unit}",
                "soil_type": farm.soil_type,
                "irrigation_type": farm.irrigation_type,
                "water_availability": farm.water_availability,
                "soil_nutrients": {
                    "nitrogen": farm.nitrogen,
                    "phosphorus": farm.phosphorus,
                    "potassium": farm.potassium,
                    "ph": farm.soil_ph,
                    "organic_carbon": farm.organic_carbon
                }
            }
            
            # Agent Contexts
            context['weather'] = get_weather_context(farm.id)
            context['market_forecast'] = get_market_context(farm.id)
            context['crop_recommendations'] = get_crop_context(farm.id)
            context['disease_history'] = get_disease_context(farm.id)
            
        except Farm.DoesNotExist:
            context['farm_details'] = "Farm not found or access denied."
    else:
        context['farm_details'] = "No specific farm selected. Provide general agricultural advice."
        
    return context
