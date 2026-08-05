import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrinova.settings")
django.setup()

from django.contrib.auth.models import User
from farms.models import Farm
from farms.serializers import FarmSerializer

def test_farm_update():
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
    
    print(f"Testing Farm ID: {farm.id}")
    
    # Simulate frontend payload sent during edit
    payload = {
        "id": farm.id,
        "name": "Updated Farm Name",
        "area": "3.5",
        "areaUnit": "Acres",
        "state": "Gujarat",
        "district": "Rajkot",
        "village": "Bediyapar",
        "soilType": "Loamy Soil",
        "nitrogen": "",
        "phosphorus": "",
        "potassium": "",
        "soil_ph": ""
    }

    serializer = FarmSerializer(instance=farm, data=payload, partial=False)
    is_valid = serializer.is_valid()
    print(f"Is PUT Valid: {is_valid}")
    if not is_valid:
        print(f"PUT Validation Errors: {serializer.errors}")

    serializer_partial = FarmSerializer(instance=farm, data=payload, partial=True)
    is_partial_valid = serializer_partial.is_valid()
    print(f"Is PATCH Valid: {is_partial_valid}")
    if not is_partial_valid:
        print(f"PATCH Validation Errors: {serializer_partial.errors}")

if __name__ == '__main__':
    test_farm_update()
