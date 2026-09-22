from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import StudentProfile


User = get_user_model()


class StudentProfileTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="studenttest@campushire.com",
            password="Student@123",
            role="STUDENT",
        )

        self.client.force_authenticate(user=self.user)

        self.profile = StudentProfile.objects.create(
            user=self.user,
            roll_number="TEST001",
            phone="9876543210",
            date_of_birth="2003-01-15",
            gender="Male",
            department="Information Technology",
            graduation_year=2027,
            cgpa=7.01,
            backlogs=0,
            bio="Test student profile.",
        )

    def test_student_can_view_own_profile(self):
        response = self.client.get(
            reverse("student-profile")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["roll_number"],
            "TEST001",
        )

    def test_student_can_update_own_profile(self):
        response = self.client.patch(
            reverse("student-profile"),
            {
                "phone": "9999999999",
                "bio": "Updated student profile.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.phone,
            "9999999999",
        )

        self.assertEqual(
            self.profile.bio,
            "Updated student profile.",
        )
