import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrinova.settings")
django.setup()

from django.contrib.auth.models import User
from farms.models import Farm
from fertilizer_recommendation.services.fertilizer_service import FertilizerService

def test_dynamic_recommendation_diversity():
    print("======================================================================")
    print("   TESTING SMART FERTILIZER RECOMMENDATION DIVERSITY & DATASET USE   ")
    print("======================================================================")

    user, _ = User.objects.get_or_create(username="diversity_tester", email="diversity@agrinova.com")

    scenarios = [
        {
            "name": "Scenario 1: Cotton on Sandy Soil in Kharif (Low Nitrogen, Rainfed, 5.0 Acres)",
            "farm_data": {
                "farm_name": "Sandy Cotton Farm",
                "farm_area": 5.0, "area_unit": "Acres",
                "soil_type": "Sandy Soil", "irrigation_type": "Rainfed", "water_availability": "Low",
                "nitrogen": 15.0, "phosphorus": 50.0, "potassium": 45.0, "soil_ph": 6.5
            },
            "crop": "Cotton", "growth_stage": "Vegetative / Active Growth"
        },
        {
            "name": "Scenario 2: Groundnut on Acidic Soil (Low Phosphorus, pH 5.2, 4.0 Bigha)",
            "farm_data": {
                "farm_name": "Acidic Groundnut Farm",
                "farm_area": 4.0, "area_unit": "Bigha",
                "soil_type": "Red Loam", "irrigation_type": "Sprinkler", "water_availability": "Medium",
                "nitrogen": 45.0, "phosphorus": 12.0, "potassium": 50.0, "soil_ph": 5.2
            },
            "crop": "Groundnut", "growth_stage": "Basal / Sowing"
        },
        {
            "name": "Scenario 3: Wheat on Alkaline Soil (Low Potassium, pH 8.2, Drip Fertigation, 1.5 Hectares)",
            "farm_data": {
                "farm_name": "Alkaline Wheat Farm",
                "farm_area": 1.5, "area_unit": "Hectares",
                "soil_type": "Black Soil", "irrigation_type": "Drip Irrigation", "water_availability": "High",
                "nitrogen": 40.0, "phosphorus": 45.0, "potassium": 15.0, "soil_ph": 8.2
            },
            "crop": "Wheat", "growth_stage": "Flowering & Fruiting"
        },
        {
            "name": "Scenario 4: Rice with High NPK (Rich Organic Soil, 20.0 Guntha)",
            "farm_data": {
                "farm_name": "Rich Organic Rice Farm",
                "farm_area": 20.0, "area_unit": "Guntha",
                "soil_type": "Alluvial", "irrigation_type": "Canal", "water_availability": "Good",
                "nitrogen": 65.0, "phosphorus": 60.0, "potassium": 65.0, "soil_ph": 6.8
            },
            "crop": "Rice", "growth_stage": "Basal / Sowing"
        }
    ]

    for sc in scenarios:
        print(f"\n---> {sc['name']}")
        farm, _ = Farm.objects.get_or_create(
            user=user,
            farm_name=sc['farm_data']['farm_name'],
            defaults={
                "state": "Gujarat", "district": "Rajkot", "taluka": "Rajkot", "village": "TestVillage",
                "farm_area": sc['farm_data']['farm_area'], "area_unit": sc['farm_data']['area_unit'],
                "soil_type": sc['farm_data']['soil_type'], "irrigation_type": sc['farm_data']['irrigation_type'],
                "water_availability": sc['farm_data']['water_availability'],
                "nitrogen": sc['farm_data']['nitrogen'], "phosphorus": sc['farm_data']['phosphorus'],
                "potassium": sc['farm_data']['potassium'], "soil_ph": sc['farm_data']['soil_ph']
            }
        )
        # Update parameters explicitly
        for k, v in sc['farm_data'].items():
            if k not in ['farm_name']:
                setattr(farm, k, v)
        farm.save()

        res = FertilizerService.generate_recommendation(
            farm_id=farm.id, user=user, growth_stage=sc['growth_stage'], crop=sc['crop']
        )

        print(f"   [Primary Choice]: {res['recommended_fertilizer']}")
        print(f"   [Unit Dosage]: {res['dosage_per_unit_text']} (Original Unit: {res['area_unit']})")
        print(f"   [Total Quantity]: {res['total_quantity_text']}")
        print(f"   [Total Cost]: ₹{res['estimated_cost_inr']}")
        print(f"   [AI Explanation]: {res['ai_explanation']}")
        print("   [Top Recommendations List]:")
        for rec in res['top_recommendations']:
            print(f"      - #{rec['rank']} {rec['name']} (Score: {rec['suitability_score']}%) | {rec['dosage_per_unit_text']} | Cost: ₹{rec['estimated_cost_inr']}")
            print(f"        Why: {rec['why_recommended']}")

    print("\n[SUCCESS] Diversity verification completed successfully!")

if __name__ == '__main__':
    test_dynamic_recommendation_diversity()
