from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Company, RecruiterProfile

User = get_user_model()


class CompanyTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            email="companyadmin@campushire.com",
            password="Admin@123",
            role="ADMIN",
        )

        self.recruiter = User.objects.create_user(
            email="companyrecruiter@campushire.com",
            password="Recruiter@123",
            role="RECRUITER",
        )

        self.student = User.objects.create_user(
            email="companystudent@campushire.com",
            password="Student@123",
            role="STUDENT",
        )

        self.company = Company.objects.create(
            name="Existing Company",
            description="Existing test company.",
            website="https://www.existingcompany.com",
            industry="Information Technology",
            location="Bengaluru, India",
            company_size="51-200",
        )

        self.company_url = reverse(
            "company-list-create"
        )

    def test_any_authenticated_user_can_view_companies(self):
        self.client.force_authenticate(
            user=self.student
        )

        response = self.client.get(
            self.company_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["name"],
            "Existing Company",
        )

    def test_admin_can_create_company(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.company_url,
            {
                "name": "New Company",
                "description": "New test company.",
                "website": "https://www.newcompany.com",
                "industry": "Information Technology",
                "location": "Pune, India",
                "company_size": "201-500",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Company.objects.filter(
                name="New Company"
            ).exists()
        )

    def test_non_admin_cannot_create_company(self):
        self.client.force_authenticate(
            user=self.recruiter
        )

        response = self.client.post(
            self.company_url,
            {
                "name": "Unauthorized Company",
                "description": "Should not be created.",
                "website": "https://www.unauthorized.com",
                "industry": "Information Technology",
                "location": "Pune, India",
                "company_size": "51-200",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_update_company(self):
        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "company-detail",
            kwargs={"pk": self.company.id},
        )

        response = self.client.patch(
            url,
            {
                "description": "Updated company description."
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.company.refresh_from_db()

        self.assertEqual(
            self.company.description,
            "Updated company description.",
        )

    def test_non_admin_cannot_update_company(self):
        self.client.force_authenticate(
            user=self.recruiter
        )

        url = reverse(
            "company-detail",
            kwargs={"pk": self.company.id},
        )

        response = self.client.patch(
            url,
            {
                "description": "Unauthorized update."
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_delete_company(self):
        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "company-detail",
            kwargs={"pk": self.company.id},
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Company.objects.filter(
                id=self.company.id
            ).exists()
        )


class RecruiterProfileTests(APITestCase):

    def setUp(self):
        self.recruiter = User.objects.create_user(
            email="profile_recruiter@campushire.com",
            password="Recruiter@123",
            role="RECRUITER",
        )

        self.student = User.objects.create_user(
            email="profile_student@campushire.com",
            password="Student@123",
            role="STUDENT",
        )

        self.company = Company.objects.create(
            name="Recruiter Profile Company",
            description="Company for recruiter profile tests.",
            website="https://www.profilecompany.com",
            industry="Information Technology",
            location="Bengaluru, India",
            company_size="51-200",
        )

        self.create_url = reverse(
            "recruiter-profile-create"
        )

        self.profile_url = reverse(
            "recruiter-profile"
        )

    def profile_payload(self):
        return {
            "company": self.company.id,
            "designation": "Campus Recruitment Manager",
            "phone": "9876543210",
            "is_primary": True,
        }

    def test_recruiter_can_create_profile(self):
        self.client.force_authenticate(
            user=self.recruiter
        )

        response = self.client.post(
            self.create_url,
            self.profile_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        profile = RecruiterProfile.objects.get(
            user=self.recruiter
        )

        self.assertEqual(
            profile.company,
            self.company,
        )

        self.assertEqual(
            profile.designation,
            "Campus Recruitment Manager",
        )

    def test_recruiter_can_view_own_profile(self):
        profile = RecruiterProfile.objects.create(
            user=self.recruiter,
            company=self.company,
            designation="Campus Recruitment Manager",
            phone="9876543210",
            is_primary=True,
        )

        self.client.force_authenticate(
            user=self.recruiter
        )

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            profile.id,
        )

        self.assertEqual(
            response.data["company_name"],
            "Recruiter Profile Company",
        )

    def test_recruiter_can_update_own_profile(self):
        RecruiterProfile.objects.create(
            user=self.recruiter,
            company=self.company,
            designation="Old Designation",
            phone="9876543210",
            is_primary=True,
        )

        self.client.force_authenticate(
            user=self.recruiter
        )

        response = self.client.patch(
            self.profile_url,
            {
                "designation": "Senior Campus Recruitment Manager"
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        profile = RecruiterProfile.objects.get(
            user=self.recruiter
        )

        self.assertEqual(
            profile.designation,
            "Senior Campus Recruitment Manager",
        )

    def test_recruiter_cannot_create_duplicate_profile(self):
        RecruiterProfile.objects.create(
            user=self.recruiter,
            company=self.company,
            designation="Campus Recruitment Manager",
            phone="9876543210",
            is_primary=True,
        )

        self.client.force_authenticate(
            user=self.recruiter
        )

        response = self.client.post(
            self.create_url,
            self.profile_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_student_cannot_create_recruiter_profile(self):
        self.client.force_authenticate(
            user=self.student
        )

        response = self.client.post(
            self.create_url,
            self.profile_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_student_cannot_access_recruiter_profile(self):
        self.client.force_authenticate(
            user=self.student
        )

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
