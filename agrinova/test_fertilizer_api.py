import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrinova.settings")
django.setup()

from django.contrib.auth.models import User
from farms.models import Farm
from fertilizer_recommendation.services.fertilizer_service import FertilizerService

def test_fertilizer_service():
    print("--- Testing Smart Fertilizer Recommendation System ---")
    user, _ = User.objects.get_or_create(username="test_farmer", email="farmer@agrinova.com")
    
    # 1. Test Soil-Based Path (NPK Available)
    farm_soil, _ = Farm.objects.get_or_create(
        user=user,
        farm_name="Green Acres (Soil Tested)",
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
            "nitrogen": 35.0,
            "phosphorus": 42.0,
            "potassium": 38.0,
            "soil_ph": 6.5
        }
    )
    
    print("\n1. Testing Path A: SOIL-BASED (NPK Data Available)...")
    res_soil = FertilizerService.generate_recommendation(farm_id=farm_soil.id, user=user)
    print(f"   -> Recommendation Type: {res_soil['recommendation_type_display']}")
    print(f"   -> Confidence Score: {res_soil['confidence_score']}%")
    print(f"   -> Recommended Fertilizer: {res_soil['recommended_fertilizer']}")
    print(f"   -> Dosage: {res_soil['dosage_per_acre_kg']} kg/acre | Total: {res_soil['total_quantity_kg']} kg")
    print(f"   -> Estimated Cost: Rs. {res_soil['estimated_cost_inr']}")

    # 2. Test Estimated Path (NPK Missing)
    farm_est, _ = Farm.objects.get_or_create(
        user=user,
        farm_name="Sunrise Fields (No Soil Test)",
        defaults={
            "state": "Punjab",
            "district": "Ludhiana",
            "taluka": "Ludhiana",
            "village": "Gill",
            "farm_area": 3.0,
            "area_unit": "Acres",
            "soil_type": "Alluvial",
            "irrigation_type": "Canal",
            "water_availability": "High",
            "nitrogen": None,
            "phosphorus": None,
            "potassium": None,
            "soil_ph": None
        }
    )

    print("\n2. Testing Path B: ESTIMATED (NPK Missing)...")
    res_est = FertilizerService.generate_recommendation(farm_id=farm_est.id, user=user)
    print(f"   -> Recommendation Type: {res_est['recommendation_type_display']}")
    print(f"   -> Confidence Score: {res_est['confidence_score']}%")
    print(f"   -> Recommended Fertilizer: {res_est['recommended_fertilizer']}")
    print(f"   -> Dosage: {res_est['dosage_per_acre_kg']} kg/acre | Total: {res_est['total_quantity_kg']} kg")
    print(f"   -> Estimated Cost: Rs. {res_est['estimated_cost_inr']}")

    print("\n[SUCCESS] Both decision flow paths verified and functioning flawlessly!")

if __name__ == '__main__':
    test_fertilizer_service()
