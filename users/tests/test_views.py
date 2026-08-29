from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewsApiTests(APITestCase):
    def setUp(self):
        # Common test data setup
        self.email = "testuser@social.com"
        self.password = "securepassword123"
        self.user = User.objects.create_user(email=self.email, password=self.password)

        self.register_url = "/api/users/register/"
        self.login_url = "/api/users/login/"
        self.profile_url = "/api/users/user_info/"

    def test_user_registration_success(self):
        """Test: A new user can register via API and receive 201 Created"""
        payload = {"email": "brandnewuser@social.com", "password": "newpassword123"}

        response = self.client.post(self.register_url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(
            User.objects.get(email="brandnewuser@social.com").email,
            "brandnewuser@social.com",
        )

    def test_user_login_success(self):
        """Test: An existing user can log in with correct credentials and get a token"""
        payload = {"username": self.email, "password": self.password}

        response = self.client.post(self.login_url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify that token is present in the response data
        self.assertIn("token", response.data)

    def test_user_login_wrong_password(self):
        """Test: Login fails with 400 or 401 when incorrect password is provided"""
        payload = {"username": self.email, "password": "wrongpassword"}

        response = self.client.post(self.login_url, payload)

        # Depending on DRF settings/views, invalid credentials usually return 400 Bad Request or 401 Unauthorized
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED],
        )

    def test_get_user_profile_authenticated(self):
        """Test: An authenticated user can successfully retrieve their profile data"""
        # Authenticate client using DRF Token authentication
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.email)

    def test_get_user_profile_unauthenticated(self):
        """Test: Unauthenticated user cannot access the profile endpoint (401)"""
        # Ensure client has no authentication
        self.client.force_authenticate(user=None)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_other_user_info_by_id(self):
        """Test: Authenticated user can view another user's info by passing ID"""
        email = "other@social.com"
        password = "password123"
        other_user = User.objects.create_user(email=email, password=password)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"{self.profile_url}{other_user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], email)

    def test_user_info_unauthenticated(self):
        """Test: Unauthenticated user cannot access user_info (401)"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
