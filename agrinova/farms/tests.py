from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from farms.models import FarmerProfile, Farm

class FarmsBackendAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testfarmer',
            email='testfarmer@agrinova.com',
            password='TestPassword123!'
        )
        self.client.force_authenticate(user=self.user)

    def test_profile_retrieval_and_update(self):
        # GET profile
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # UPDATE profile
        payload = {
            "fullName": "Ramesh Patil",
            "phone": "+919876543210",
            "language": "Marathi"
        }
        response = self.client.post('/api/profile/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data']['profile_completed'])
        self.assertEqual(response.data['data']['full_name'], "Ramesh Patil")
        self.assertEqual(response.data['data']['phone_number'], "+919876543210")

    def test_farm_crud_and_geocoding(self):
        farm_payload = {
            "name": "Green Acres",
            "area": "15.5",
            "areaUnit": "Acres",
            "state": "Madhya Pradesh",
            "district": "Bhopal",
            "taluka": "Huzur",
            "village": "Khajuri",
            "pinCode": "462001",
            "soilType": "Black Soil",
            "irrigationType": "Drip Irrigation",
            "waterAvailability": "Moderate / Seasonal"
        }

        # Create Farm 1 (First farm should automatically be active)
        response = self.client.post('/api/farms/', farm_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        farm1_id = response.data['data']['id']
        self.assertTrue(response.data['data']['is_active'])
        self.assertEqual(response.data['data']['farm_name'], "Green Acres")

        # Create Farm 2
        farm_payload2 = {
            "name": "Riverbed Farm",
            "area": "8.0",
            "areaUnit": "Acres",
            "state": "Madhya Pradesh",
            "district": "Indore",
            "taluka": "Depalpur",
            "village": "Betma",
            "soilType": "Alluvial Soil",
            "irrigationType": "Canal Irrigation",
            "waterAvailability": "Abundant / Year-round"
        }
        response2 = self.client.post('/api/farms/', farm_payload2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        farm2_id = response2.data['data']['id']
        self.assertFalse(response2.data['data']['is_active'])

        # LIST Farms
        list_response = self.client.get('/api/farms/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['data']), 2)

        # SELECT Farm 2 as active
        select_response = self.client.post(f'/api/farms/select/{farm2_id}/')
        self.assertEqual(select_response.status_code, status.HTTP_200_OK)
        self.assertTrue(select_response.data['data']['is_active'])

        # Verify Farm 1 is now inactive
        farm1_obj = Farm.objects.get(pk=farm1_id)
        self.assertFalse(farm1_obj.is_active)

    def test_dashboard_endpoint(self):
        # Create profile and farm first
        FarmerProfile.objects.create(
            user=self.user,
            full_name="Ramesh Patil",
            phone_number="9876543210",
            preferred_language="Hindi",
            profile_completed=True
        )
        Farm.objects.create(
            user=self.user,
            farm_name="Sunset Plot",
            state="Maharashtra",
            district="Nashik",
            taluka="Niphad",
            village="Pimpalgaon",
            farm_area=12.0,
            soil_type="Black Soil",
            irrigation_type="Drip",
            water_availability="Seasonal",
            is_active=True
        )

        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['total_farms'], 1)
        self.assertTrue(response.data['data']['profile_completed'])
        self.assertEqual(response.data['data']['selected_farm']['farm_name'], "Sunset Plot")
