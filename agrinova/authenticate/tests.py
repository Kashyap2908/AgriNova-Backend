from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationTests(APITestCase):
    """
    Test suite for authenticate app.
    Covers registration, login (username/email), profile, and logout token blacklisting.
    """

    def setUp(self):
        self.register_url = reverse('authenticate:register')
        self.login_url = reverse('authenticate:login')
        self.profile_url = reverse('authenticate:profile')
        self.logout_url = reverse('authenticate:logout')

        self.valid_user_data = {
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "User registered successfully")
        self.assertEqual(response.data['data']['user']['username'], "johndoe")
        self.assertEqual(response.data['data']['user']['email'], "johndoe@example.com")
        self.assertNotIn('password', response.data['data']['user'])

    def test_user_registration_password_mismatch(self):
        data = self.valid_user_data.copy()
        data['confirm_password'] = "Mismatch123!"
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('confirm_password', response.data['errors'])

    def test_user_registration_duplicate_fields(self):
        # Register first user
        self.client.post(self.register_url, self.valid_user_data, format='json')

        # Try registering with same username
        data = self.valid_user_data.copy()
        data['email'] = "other@example.com"
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data['errors'])

        # Try registering with same email
        data = self.valid_user_data.copy()
        data['username'] = "otheruser"
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_login_success_with_username(self):
        # Create user
        User.objects.create_user(
            username="johndoe",
            email="johndoe@example.com",
            password="Password123!"
        )

        login_data = {
            "username": "johndoe",
            "password": "Password123!"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['data']['user']['username'], "johndoe")

    def test_login_success_with_email(self):
        # Create user
        User.objects.create_user(
            username="johndoe",
            email="johndoe@example.com",
            password="Password123!"
        )

        login_data = {
            "username": "johndoe@example.com",
            "password": "Password123!"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])

    def test_login_failure_invalid_credentials(self):
        User.objects.create_user(
            username="johndoe",
            email="johndoe@example.com",
            password="Password123!"
        )

        login_data = {
            "username": "johndoe",
            "password": "WrongPassword123"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], "Invalid credentials. Please check your username/email and password.")

    def test_profile_access_success(self):
        user = User.objects.create_user(
            username="johndoe",
            email="johndoe@example.com",
            password="Password123!"
        )
        # Login to get token
        login_data = {"username": "johndoe", "password": "Password123!"}
        login_res = self.client.post(self.login_url, login_data, format='json')
        access_token = login_res.data['data']['access']

        # Set auth header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['username'], "johndoe")

    def test_profile_access_denied_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])

    def test_logout_success_blacklist_token(self):
        user = User.objects.create_user(
            username="johndoe",
            email="johndoe@example.com",
            password="Password123!"
        )
        # Login to get tokens
        login_data = {"username": "johndoe", "password": "Password123!"}
        login_res = self.client.post(self.login_url, login_data, format='json')
        access_token = login_res.data['data']['access']
        refresh_token = login_res.data['data']['refresh']

        # Set auth header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Logout using refresh token
        logout_res = self.client.post(self.logout_url, {"refresh": refresh_token}, format='json')
        self.assertEqual(logout_res.status_code, status.HTTP_200_OK)
        self.assertTrue(logout_res.data['success'])

        # Attempt to use the same refresh token again to logout (should fail)
        retry_logout_res = self.client.post(self.logout_url, {"refresh": refresh_token}, format='json')
        self.assertEqual(retry_logout_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(retry_logout_res.data['success'])
