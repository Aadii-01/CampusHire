from django.test import TestCase

# Create your tests here.
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from companies.models import Company, RecruiterProfile
from skills.models import Skill, StudentSkill
from students.models import StudentProfile

from .models import Job, JobEligibility, JobRequiredSkill


User = get_user_model()


class JobEligibilityTests(APITestCase):

    def setUp(self):
        self.recruiter = User.objects.create_user(
            email="recruitertest@campushire.com",
            password="Recruiter@123",
            role="RECRUITER",
        )

        self.student = User.objects.create_user(
            email="studenteligibility@campushire.com",
            password="Student@123",
            role="STUDENT",
        )

        self.company = Company.objects.create(
            name="Test Company",
            description="Test company for automated tests.",
            website="https://www.testcompany.com",
            industry="Information Technology",
            location="Bengaluru, India",
            company_size="51-200",
        )

        RecruiterProfile.objects.create(
            user=self.recruiter,
            company=self.company,
            designation="Campus Recruitment Manager",
            phone="9876543210",
            is_primary=True,
        )

        StudentProfile.objects.create(
            user=self.student,
            roll_number="TESTELIG001",
            phone="9876543211",
            date_of_birth="2003-01-15",
            gender="Male",
            department="Information Technology",
            graduation_year=2027,
            cgpa=7.01,
            backlogs=0,
            bio="Eligibility test student.",
        )

        self.python = Skill.objects.create(
            name="Python"
        )

        self.django = Skill.objects.create(
            name="Django"
        )

        self.job = Job.objects.create(
            company=self.company,
            recruiter=self.recruiter,
            title="Test Software Engineer",
            description="Test job for eligibility.",
            employment_type="FULL_TIME",
            work_mode="ONSITE",
            location="Bengaluru, India",
            salary_min=600000,
            salary_max=900000,
            application_deadline=(
                timezone.now() + timedelta(days=30)
            ),
            status="OPEN",
        )

        JobEligibility.objects.create(
            job=self.job,
            min_cgpa=Decimal("6.50"),
            max_backlogs=2,
            graduation_year=2027,
            allowed_departments=[
                "Information Technology",
                "Computer Science",
            ],
        )

        JobRequiredSkill.objects.create(
            job=self.job,
            skill=self.python,
            required_proficiency="INTERMEDIATE",
        )

        JobRequiredSkill.objects.create(
            job=self.job,
            skill=self.django,
            required_proficiency="INTERMEDIATE",
        )

    def test_eligible_student_passes_all_criteria(self):
        StudentSkill.objects.create(
            student=self.student,
            skill=self.python,
            proficiency="INTERMEDIATE",
        )

        StudentSkill.objects.create(
            student=self.student,
            skill=self.django,
            proficiency="INTERMEDIATE",
        )

        self.client.force_authenticate(
            user=self.student
        )

        response = self.client.get(
            reverse(
                "job-eligibility-check",
                kwargs={"job_id": self.job.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["eligible"]
        )

        self.assertEqual(
            response.data["failed_criteria"],
            [],
        )

        self.assertEqual(
            response.data["missing_skills"],
            [],
        )

    def test_student_with_missing_skill_is_ineligible(self):
        StudentSkill.objects.create(
            student=self.student,
            skill=self.python,
            proficiency="INTERMEDIATE",
        )

        self.client.force_authenticate(
            user=self.student
        )

        response = self.client.get(
            reverse(
                "job-eligibility-check",
                kwargs={"job_id": self.job.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["eligible"]
        )

        self.assertEqual(
            len(response.data["missing_skills"]),
            1,
        )

        self.assertEqual(
            response.data["missing_skills"][0]["skill"],
            "Django",
        )

    def test_student_with_insufficient_proficiency_is_ineligible(self):
        StudentSkill.objects.create(
            student=self.student,
            skill=self.python,
            proficiency="BEGINNER",
        )

        StudentSkill.objects.create(
            student=self.student,
            skill=self.django,
            proficiency="INTERMEDIATE",
        )

        self.client.force_authenticate(
            user=self.student
        )

        response = self.client.get(
            reverse(
                "job-eligibility-check",
                kwargs={"job_id": self.job.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["eligible"]
        )

        self.assertEqual(
            len(response.data["missing_skills"]),
            1,
        )

        self.assertEqual(
            response.data["missing_skills"][0]["skill"],
            "Python",
        )

    def test_student_with_failed_academic_criteria_is_ineligible(self):
        profile = self.student.student_profile

        profile.cgpa = 6.00
        profile.backlogs = 3
        profile.graduation_year = 2026
        profile.department = "Mechanical Engineering"
        profile.save()

        StudentSkill.objects.create(
            student=self.student,
            skill=self.python,
            proficiency="INTERMEDIATE",
        )

        StudentSkill.objects.create(
            student=self.student,
            skill=self.django,
            proficiency="INTERMEDIATE",
        )

        self.client.force_authenticate(
            user=self.student
        )

        response = self.client.get(
            reverse(
                "job-eligibility-check",
                kwargs={"job_id": self.job.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["eligible"]
        )

        failed_criteria = response.data[
            "failed_criteria"
        ]

        criteria = [
            item["criterion"]
            for item in failed_criteria
        ]

        self.assertIn("CGPA", criteria)
        self.assertIn("Backlogs", criteria)
        self.assertIn(
            "Graduation Year",
            criteria,
        )
        self.assertIn(
            "Department",
            criteria,
        )

    def test_non_student_cannot_check_eligibility(self):
        self.client.force_authenticate(
            user=self.recruiter
        )

        response = self.client.get(
            reverse(
                "job-eligibility-check",
                kwargs={"job_id": self.job.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
