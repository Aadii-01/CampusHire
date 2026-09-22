from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Skill, StudentSkill


User = get_user_model()


class StudentSkillTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="skilltest@campushire.com",
            password="Skill@123",
            role="STUDENT",
        )

        self.client.force_authenticate(user=self.user)

        self.python = Skill.objects.create(
            name="Python"
        )

        self.django = Skill.objects.create(
            name="Django"
        )

    def test_student_can_list_skills(self):
        StudentSkill.objects.create(
            student=self.user,
            skill=self.python,
            proficiency="INTERMEDIATE",
        )

        response = self.client.get(
            reverse("student-skill-list-create")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_student_skill_is_created(self):
        response = self.client.post(
            reverse("student-skill-list-create"),
            {
                "skill": self.python.id,
                "proficiency": "INTERMEDIATE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            StudentSkill.objects.filter(
                student=self.user,
                skill=self.python,
            ).exists()
        )
