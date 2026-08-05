import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrinova.settings")
django.setup()

from django.contrib.auth.models import User
from farms.models import Farm
from farms.serializers import FarmSerializer

def test_patch_farm():
    print("--- Testing Farm PATCH Edit Functionality ---")
    user, _ = User.objects.get_or_create(username="test_farmer")
    farm = Farm.objects.filter(user=user).first()
    if not farm:
        farm = Farm.objects.create(
            user=user,
            farm_name="Test Farm",
            state="Gujarat",
            district="Rajkot",
            taluka="Rajkot",
            village="Bediyapar",
            farm_area=2.5,
            soil_type="Loamy",
            irrigation_type="Drip",
            water_availability="Good"
        )

    # Test payload sent during edit (simulating React state with empty strings for blank soil fields)
    patch_payload = {
        "name": "Green Acres - Updated",
        "area": "3.5",
        "areaUnit": "Acres",
        "state": "Gujarat",
        "district": "Rajkot",
        "village": "Bediyapar",
        "soilType": "Black Soil",
        "nitrogen": "45.0",
        "phosphorus": "35.0",
        "potassium": "",
        "soil_ph": "6.8"
    }

    serializer = FarmSerializer(instance=farm, data=patch_payload, partial=True)
    is_valid = serializer.is_valid()
    print(f"Is PATCH Valid: {is_valid}")
    if not is_valid:
        print(f"Errors: {serializer.errors}")
    else:
        updated_farm = serializer.save()
        print(f"Saved Farm Name: '{updated_farm.farm_name}'")
        print(f"Saved Area: {updated_farm.farm_area} {updated_farm.area_unit}")
        print(f"Saved Soil: {updated_farm.soil_type}")
        print(f"Saved Nitrogen: {updated_farm.nitrogen}")
        print(f"Saved Phosphorus: {updated_farm.phosphorus}")
        print(f"Saved Potassium (cleared): {updated_farm.potassium}")
        print(f"Saved pH: {updated_farm.soil_ph}")
        print("[SUCCESS] Farm PATCH edit works flawlessly!")

if __name__ == '__main__':
    test_patch_farm()
