import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrinova.settings")
django.setup()

from django.contrib.auth.models import User
from farms.models import Farm
from fertilizer_recommendation.services.fertilizer_service import FertilizerService

def test_farm_data_change():
    print("=== TESTING FERTILIZER RECOMMENDATION AFTER FARM DATA EDIT ===")
    user, _ = User.objects.get_or_create(username="farm_edit_tester", email="edit_tester@agrinova.com")
    
    # Create farm
    farm, _ = Farm.objects.get_or_create(
        user=user,
        farm_name="Dynamic Test Farm",
        defaults={
            "state": "Gujarat",
            "district": "Rajkot",
            "taluka": "Rajkot",
            "village": "Bediyapar",
            "farm_area": 2.0,
            "area_unit": "Acres",
            "soil_type": "Loamy Soil",
            "irrigation_type": "Drip Irrigation",
            "water_availability": "Good",
            "nitrogen": 15.0,
            "phosphorus": 55.0,
            "potassium": 50.0,
            "soil_ph": 6.5
        }
    )

    print("\n--- 1. Initial State: Low Nitrogen (N=15, P=55, K=50) ---")
    farm.nitrogen = 15.0
    farm.phosphorus = 55.0
    farm.potassium = 50.0
    farm.soil_ph = 6.5
    farm.save()

    res1 = FertilizerService.generate_recommendation(farm_id=farm.id, user=user)
    print(f"   Recommended: {res1['recommended_fertilizer']}")
    print(f"   Dosage: {res1['dosage_per_acre_kg']} kg/acre | Total: {res1['total_quantity_kg']} kg")

    print("\n--- 2. Edit Farm: Low Phosphorus (N=55, P=10, K=50) ---")
    farm.nitrogen = 55.0
    farm.phosphorus = 10.0
    farm.potassium = 50.0
    farm.soil_ph = 6.5
    farm.save()

    res2 = FertilizerService.generate_recommendation(farm_id=farm.id, user=user)
    print(f"   Recommended: {res2['recommended_fertilizer']}")
    print(f"   Dosage: {res2['dosage_per_acre_kg']} kg/acre | Total: {res2['total_quantity_kg']} kg")

    print("\n--- 3. Edit Farm: Low Potassium (N=55, P=50, K=10) ---")
    farm.nitrogen = 55.0
    farm.phosphorus = 50.0
    farm.potassium = 10.0
    farm.soil_ph = 6.5
    farm.save()

    res3 = FertilizerService.generate_recommendation(farm_id=farm.id, user=user)
    print(f"   Recommended: {res3['recommended_fertilizer']}")
    print(f"   Dosage: {res3['dosage_per_acre_kg']} kg/acre | Total: {res3['total_quantity_kg']} kg")

    print("\n--- 4. Edit Farm: Acidic Soil (pH=5.2) ---")
    farm.soil_ph = 5.2
    farm.save()

    res4 = FertilizerService.generate_recommendation(farm_id=farm.id, user=user)
    print(f"   Recommended: {res4['recommended_fertilizer']}")
    print(f"   Dosage: {res4['dosage_per_acre_kg']} kg/acre | Total: {res4['total_quantity_kg']} kg")

if __name__ == '__main__':
    test_farm_data_change()
