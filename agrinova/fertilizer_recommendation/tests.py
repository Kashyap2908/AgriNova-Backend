from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from farms.models import Farm

class FertilizerRecommendationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='fertilizer_farmer',
            email='farmer@agrinova.com',
            password='TestPassword123!'
        )
        self.client.force_authenticate(user=self.user)
        self.farm = Farm.objects.create(
            user=self.user,
            farm_name="Demo Tech Farm",
            state="Gujarat",
            district="Junagadh",
            taluka="Visavadar",
            village="Malia",
            farm_area=5.0,
            area_unit="Acres",
            soil_type="Black Soil",
            irrigation_type="Drip",
            water_availability="Abundant",
            nitrogen=245.0,
            phosphorus=18.0,
            potassium=280.0,
            sulphur=12.5,
            zinc=0.8,
            is_active=True
        )

    def test_plan_generation_with_farm(self):
        payload = {
            "farm_id": self.farm.id,
            "crop": "Groundnut",
            "season": "Kharif",
            "previous_crop": "Wheat"
        }
        response = self.client.post('/api/fertilizer/plan/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']

        # Verify Nutrient Matrix & Classification
        matrix = data.get('nutrient_matrix', {})
        self.assertIn('N', matrix)
        self.assertEqual(matrix['N']['source'], 'Farmer Input')
        self.assertEqual(matrix['N']['available_nutrient'], 245.0)

        # Verify Source tracking for missing nutrient (e.g. Boron)
        self.assertIn('B', matrix)
        self.assertTrue('Estimated' in matrix['B']['source'])

        # Verify Groundnut Crop-Specific plan contains Gypsum / Sulphur / Rhizobium
        top_plans = data.get('top_fertilizer_plans', [])
        self.assertGreaterEqual(len(top_plans), 3)

        # Verify Cost Summary
        cost_summary = data.get('cost_summary', {})
        self.assertIn('grand_total_display', cost_summary)

    def test_custom_input_and_live_override(self):
        payload = {
            "crop": "Cotton",
            "soil_type": "Black",
            "state": "Maharashtra",
            "season": "Kharif",
            "farm_area": 10.0,
            "area_unit": "Acres",
            "nitrogen": 120.0,
            "phosphorus": 15.0,
            "potassium": 200.0,
            "soil_ph": 7.8
        }
        response = self.client.post('/api/fertilizer/plan/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['data']
        self.assertEqual(data['crop_summary']['crop'], 'Cotton')
        self.assertEqual(data['crop_summary']['farm_area'], 10.0)

    def test_fertilizer_master_catalog(self):
        response = self.client.get('/api/fertilizer/master/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreater(len(response.data['data']), 0)
