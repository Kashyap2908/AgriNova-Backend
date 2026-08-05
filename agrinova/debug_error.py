import os
import django
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrinova.settings")
django.setup()

from django.contrib.auth.models import User
from farms.models import Farm
from fertilizer_recommendation.services.fertilizer_service import FertilizerService

def debug_recommendation():
    user = User.objects.first()
    farm = Farm.objects.filter(user=user).first()
    
    print(f"User: {user}, Farm: {farm}")
    try:
        res = FertilizerService.generate_recommendation(
            farm_id=farm.id,
            user=user,
            growth_stage="Grain Filling / Fruit Set"
        )
        print("Success:", res['recommended_fertilizer'])
    except Exception as e:
        print("\n--- EXCEPTION CAUGHT ---")
        traceback.print_exc()

if __name__ == '__main__':
    debug_recommendation()
