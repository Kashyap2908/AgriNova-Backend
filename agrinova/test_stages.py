import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrinova.settings")
django.setup()

from django.contrib.auth.models import User
from farms.models import Farm
from fertilizer_recommendation.services.fertilizer_service import FertilizerService

def test_stage_variations():
    print("--- Testing Growth Stage Variations for Fertilizer Recommendation ---")
    user, _ = User.objects.get_or_create(username="stage_test_farmer", email="stage@agrinova.com")
    
    farm, _ = Farm.objects.get_or_create(
        user=user,
        farm_name="Stage Test Farm",
        defaults={
            "state": "Gujarat",
            "district": "Rajkot",
            "taluka": "Rajkot",
            "village": "Bediyapar",
            "farm_area": 2.5,
            "area_unit": "Acres",
            "soil_type": "Loamy",
            "irrigation_type": "Drip",
            "water_availability": "Good",
            "nitrogen": 30.0,
            "phosphorus": 30.0,
            "potassium": 30.0,
            "soil_ph": 6.5
        }
    )

    stages = [
        "Basal / Sowing",
        "Vegetative / Active Growth",
        "Flowering & Fruiting"
    ]

    for stg in stages:
        res = FertilizerService.generate_recommendation(farm_id=farm.id, user=user, growth_stage=stg, crop="Rice")
        print(f"\nStage: '{stg}'")
        print(f"   -> Recommended Fertilizer: {res['recommended_fertilizer']}")
        print(f"   -> Dosage per acre: {res['dosage_per_acre_kg']} kg/acre")
        print(f"   -> Ideal Nutrients (N-P-K): {res['nutrient_analysis']['nitrogen']['ideal']} - {res['nutrient_analysis']['phosphorus']['ideal']} - {res['nutrient_analysis']['potassium']['ideal']}")

if __name__ == '__main__':
    test_stage_variations()
