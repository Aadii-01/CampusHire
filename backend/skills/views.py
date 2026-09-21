from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from .models import Skill, StudentSkill
from .serializers import (
    SkillSerializer,
    StudentSkillSerializer,
)


class SkillListCreateView(generics.ListCreateAPIView):

    queryset = Skill.objects.all().order_by("name")
    serializer_class = SkillSerializer

    def perform_create(self, serializer):
        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only admins can create skills."
            )

        serializer.save()


class StudentSkillListCreateView(generics.ListCreateAPIView):

    serializer_class = StudentSkillSerializer

    def get_queryset(self):
        return StudentSkill.objects.filter(
            student=self.request.user
        ).select_related("skill")

    def perform_create(self, serializer):
        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can add skills."
            )

        serializer.save(
            student=self.request.user
        )


class StudentSkillDeleteView(generics.DestroyAPIView):

    serializer_class = StudentSkillSerializer

    def get_queryset(self):
        return StudentSkill.objects.filter(
            student=self.request.user
        )
