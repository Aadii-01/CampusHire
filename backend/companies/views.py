from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from .models import Company, RecruiterProfile
from .serializers import (
    CompanySerializer,
    RecruiterProfileSerializer,
)


# ============================================================
# COMPANY
# ============================================================

class CompanyListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = CompanySerializer

    def get_queryset(self):

        return Company.objects.all().order_by(
            "name"
        )

    def perform_create(self, serializer):

        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only admins can create companies."
            )

        serializer.save()


class CompanyDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = CompanySerializer

    def get_queryset(self):

        return Company.objects.all()

    def perform_update(self, serializer):

        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only admins can update companies."
            )

        serializer.save()

    def perform_destroy(self, instance):

        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only admins can delete companies."
            )

        instance.delete()


# ============================================================
# RECRUITER PROFILE
# ============================================================

class RecruiterProfileCreateView(
    generics.CreateAPIView
):

    serializer_class = RecruiterProfileSerializer

    def perform_create(self, serializer):

        if self.request.user.role != "RECRUITER":
            raise PermissionDenied(
                "Only recruiters can create recruiter profiles."
            )

        if RecruiterProfile.objects.filter(
            user=self.request.user
        ).exists():

            raise PermissionDenied(
                "Recruiter profile already exists."
            )

        serializer.save(
            user=self.request.user
        )


class RecruiterProfileView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = RecruiterProfileSerializer

    def get_object(self):

        if self.request.user.role != "RECRUITER":
            raise PermissionDenied(
                "Only recruiters can access recruiter profiles."
            )

        return RecruiterProfile.objects.get(
            user=self.request.user
        )

    def perform_update(self, serializer):

        serializer.save(
            user=self.request.user
        )
