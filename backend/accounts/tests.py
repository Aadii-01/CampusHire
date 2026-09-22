from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.register_url = reverse("register")
        self.token_url = reverse("token_obtain_pair")
        self.me_url = reverse("me")

        self.user_data = {
            "email": "teststudent@campushire.com",
            "password": "TestStudent@123",
            "password2": "TestStudent@123",
            "first_name": "Test",
            "last_name": "Student",
            "role": "STUDENT",
        }

    def test_student_registration(self):
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(
                email="teststudent@campushire.com"
            ).exists()
        )

    def test_jwt_login(self):
        User.objects.create_user(
            email="teststudent@campushire.com",
            password="TestStudent@123",
            role="STUDENT",
        )

        response = self.client.post(
            self.token_url,
            {
                "email": "teststudent@campushire.com",
                "password": "TestStudent@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_authenticated_me_endpoint(self):
        user = User.objects.create_user(
            email="teststudent@campushire.com",
            password="TestStudent@123",
            role="STUDENT",
        )

        response = self.client.post(
            self.token_url,
            {
                "email": "teststudent@campushire.com",
                "password": "TestStudent@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user.email)
