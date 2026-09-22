from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from drf_spectacular.utils import extend_schema


from applications.models import Application, Interview, Offer
from applications.serializers import (
    ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer,
    InterviewSerializer,
    InterviewStatusUpdateSerializer,
    OfferSerializer,
)

@extend_schema(tags=["Applications"])
class StudentApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            student=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save()

@extend_schema(tags=["Applications"])
class StudentApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            student=self.request.user
        )

@extend_schema(tags=["Applications"])
class RecruiterJobApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(
            job_id=self.kwargs["job_id"],
            job__recruiter=self.request.user,
        )

@extend_schema(tags=["Admin / TPO"])
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

@extend_schema(tags=["Interviews"])
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

@extend_schema(tags=["Interviews"])
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


@extend_schema(tags=["Interviews"])
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

@extend_schema(tags=["Interviews"])
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

@extend_schema(tags=["Interviews"])
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


@extend_schema(tags=["Interviews"])
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


@extend_schema(tags=["Offers"])
class AdminOfferCreateView(generics.CreateAPIView):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != "ADMIN":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only TPO/Admin users can create offers."
            )

        offer = serializer.save()

        application = offer.application

        if application.status == Application.Status.SELECTED:
            application.status = Application.Status.OFFERED
            application.save(
                update_fields=["status", "updated_at"]
            )

@extend_schema(tags=["Admin / TPO"])
class AdminApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != "ADMIN":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only TPO/Admin users can view all applications."
            )

        queryset = Application.objects.all().select_related(
            "student",
            "job",
            "resume",
        )

        status = self.request.query_params.get("status")
        job_id = self.request.query_params.get("job")

        if status:
            queryset = queryset.filter(status=status)

        if job_id:
            queryset = queryset.filter(job_id=job_id)

        return queryset







# ============================================================
# ADMIN / TPO DASHBOARD
# ============================================================
from rest_framework.response import Response
from django.db.models import Count

from students.models import StudentProfile
from jobs.models import Job

@extend_schema(tags=["Admin / TPO"], responses=dict,)
class AdminDashboardView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        if request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only TPO/Admin users can access the dashboard."
            )

        # ----------------------------------------------------
        # STUDENTS
        # ----------------------------------------------------

        total_students = StudentProfile.objects.count()

        students_by_department = (
            StudentProfile.objects
            .values("department")
            .annotate(total=Count("id"))
            .order_by("department")
        )

        students_by_graduation_year = (
            StudentProfile.objects
            .values("graduation_year")
            .annotate(total=Count("id"))
            .order_by("graduation_year")
        )

        # ----------------------------------------------------
        # JOBS
        # ----------------------------------------------------

        total_jobs = Job.objects.count()

        jobs_by_status = (
            Job.objects
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )

        # ----------------------------------------------------
        # APPLICATIONS
        # ----------------------------------------------------

        total_applications = Application.objects.count()

        applications_by_status = (
            Application.objects
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )

        # ----------------------------------------------------
        # INTERVIEWS
        # ----------------------------------------------------

        total_interviews = Interview.objects.count()

        interviews_by_status = (
            Interview.objects
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )

        # ----------------------------------------------------
        # OFFERS
        # ----------------------------------------------------

        total_offers = Offer.objects.count()

        offers_by_employment_type = (
            Offer.objects
            .values("employment_type")
            .annotate(total=Count("id"))
            .order_by("employment_type")
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return Response({
            "students": {
                "total": total_students,
                "by_department": list(
                    students_by_department
                ),
                "by_graduation_year": list(
                    students_by_graduation_year
                ),
            },

            "jobs": {
                "total": total_jobs,
                "by_status": list(
                    jobs_by_status
                ),
            },

            "applications": {
                "total": total_applications,
                "by_status": list(
                    applications_by_status
                ),
            },

            "interviews": {
                "total": total_interviews,
                "by_status": list(
                    interviews_by_status
                ),
            },

            "offers": {
                "total": total_offers,
                "by_employment_type": list(
                    offers_by_employment_type
                ),
            },
        })
