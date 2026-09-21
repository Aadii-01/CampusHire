from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from applications.models import Application, Interview
from applications.serializers import (
    ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer,
    InterviewSerializer,
    InterviewStatusUpdateSerializer,
)

class StudentApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            student=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save()

class StudentApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            student=self.request.user
        )

class RecruiterJobApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            job_id=self.kwargs["job_id"],
            job__recruiter=self.request.user,
        )

class AdminApplicationStatusUpdateView(generics.UpdateAPIView):
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.all()

    def perform_update(self, serializer):
        if self.request.user.role != "ADMIN":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only TPO/Admin users can update application status."
            )

        serializer.save()


class AdminInterviewCreateView(generics.CreateAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != "ADMIN":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only TPO/Admin users can schedule interviews."
            )

        interview = serializer.save()

        application = interview.application

        if application.status == Application.Status.SHORTLISTED:
            application.status = Application.Status.INTERVIEW
            application.save(update_fields=["status", "updated_at"])


class StudentInterviewListView(generics.ListAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Interview.objects.filter(
            application__student=self.request.user
        ).select_related(
            "application",
            "application__job",
        )


class RecruiterInterviewListView(generics.ListAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Interview.objects.filter(
            application__job__recruiter=self.request.user
        ).select_related(
            "application",
            "application__job",
        )


class AdminInterviewListView(generics.ListAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "ADMIN":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only TPO/Admin users can view all interviews."
            )

        return Interview.objects.all().select_related(
            "application",
            "application__job",
        )

class AdminInterviewUpdateView(generics.UpdateAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "ADMIN":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only TPO/Admin users can update interviews."
            )

        return Interview.objects.all()

class AdminInterviewStatusUpdateView(generics.UpdateAPIView):
    serializer_class = InterviewStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "ADMIN":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only TPO/Admin users can update interview status."
            )

        return Interview.objects.all()
