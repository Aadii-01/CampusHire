from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import (
    StudentProfile,
    Education,
    Project,
    Experience,
    Resume,
)

from .serializers import (
    StudentProfileSerializer,
    EducationSerializer,
    ProjectSerializer,
    ExperienceSerializer,
    ResumeSerializer,
    StudentDashboardSerializer,
)


# ============================================================
# STUDENT PROFILE
# ============================================================
@extend_schema(tags=["Students"])
class StudentProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = StudentProfileSerializer

    def get_object(self):
        try:
            return StudentProfile.objects.get(
                user=self.request.user
            )
        except StudentProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Student profile does not exist."
            )

    def perform_update(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can update a student profile."
            )

        profile = serializer.save()

        profile.update_profile_completion()

@extend_schema(tags=["Students"])
class StudentProfileCreateView(generics.CreateAPIView):

    serializer_class = StudentProfileSerializer

    def perform_create(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can create a student profile."
            )

        if StudentProfile.objects.filter(
            user=self.request.user
        ).exists():

            raise PermissionDenied(
                "Student profile already exists."
            )

        profile = serializer.save(
            user=self.request.user
        )

        profile.update_profile_completion()


# ============================================================
# EDUCATION
# ============================================================
@extend_schema(tags=["Students"])
class EducationListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = EducationSerializer

    def get_queryset(self):

        return Education.objects.filter(
            student__user=self.request.user
        ).order_by(
            "-end_year",
            "-start_year"
        )

    def perform_create(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can add education."
            )

        try:
            profile = StudentProfile.objects.get(
                user=self.request.user
            )
        except StudentProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Create your student profile first."
            )

        education = serializer.save(
            student=profile
        )

        profile.update_profile_completion()

@extend_schema(tags=["Students"])
class EducationDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = EducationSerializer

    def get_queryset(self):

        return Education.objects.filter(
            student__user=self.request.user
        )

    def perform_update(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can update education."
            )

        education = serializer.save()

        education.student.update_profile_completion()

    def perform_destroy(self, instance):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can delete education."
            )

        student = instance.student

        instance.delete()

        student.update_profile_completion()


# ============================================================
# PROJECTS
# ============================================================
@extend_schema(tags=["Students"])
class ProjectListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = ProjectSerializer

    def get_queryset(self):

        return Project.objects.filter(
            student__user=self.request.user
        ).order_by(
            "-start_date",
            "-created_at"
        )

    def perform_create(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can add projects."
            )

        try:
            profile = StudentProfile.objects.get(
                user=self.request.user
            )
        except StudentProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Create your student profile first."
            )

        project = serializer.save(
            student=profile
        )

        profile.update_profile_completion()

@extend_schema(tags=["Students"])
class ProjectDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ProjectSerializer

    def get_queryset(self):

        return Project.objects.filter(
            student__user=self.request.user
        )

    def perform_update(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can update projects."
            )

        project = serializer.save()

        project.student.update_profile_completion()

    def perform_destroy(self, instance):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can delete projects."
            )

        student = instance.student

        instance.delete()

        student.update_profile_completion()


# ============================================================
# EXPERIENCE
# ============================================================
@extend_schema(tags=["Students"])
class ExperienceListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = ExperienceSerializer

    def get_queryset(self):

        return Experience.objects.filter(
            student__user=self.request.user
        ).order_by(
            "-start_date",
            "-created_at"
        )

    def perform_create(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can add experience."
            )

        try:
            profile = StudentProfile.objects.get(
                user=self.request.user
            )
        except StudentProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Create your student profile first."
            )

        experience = serializer.save(
            student=profile
        )

        profile.update_profile_completion()

@extend_schema(tags=["Students"])
class ExperienceDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ExperienceSerializer

    def get_queryset(self):

        return Experience.objects.filter(
            student__user=self.request.user
        )

    def perform_update(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can update experience."
            )

        experience = serializer.save()

        experience.student.update_profile_completion()

    def perform_destroy(self, instance):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can delete experience."
            )

        student = instance.student

        instance.delete()

        student.update_profile_completion()


# ============================================================
# RESUMES
# ============================================================
@extend_schema(tags=["Students"])
class ResumeListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = ResumeSerializer

    def get_queryset(self):

        return Resume.objects.filter(
            student__user=self.request.user
        ).order_by(
            "-uploaded_at"
        )

    def perform_create(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can upload resumes."
            )

        try:
            profile = StudentProfile.objects.get(
                user=self.request.user
            )
        except StudentProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Create your student profile first."
            )

        latest_version = (
            Resume.objects
            .filter(student=profile)
            .order_by("-version")
            .values_list(
                "version",
                flat=True
            )
            .first()
        )

        next_version = (
            latest_version + 1
            if latest_version is not None
            else 1
        )

        resume = serializer.save(
            student=profile,
            version=next_version,
            file_size=self.request.FILES["file"].size,
        )

        # Only one resume can be active.
        if resume.is_active:

            Resume.objects.filter(
                student=profile
            ).exclude(
                id=resume.id
            ).update(
                is_active=False
            )

        profile.update_profile_completion()

@extend_schema(tags=["Students"])
class ResumeDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ResumeSerializer

    def get_queryset(self):

        return Resume.objects.filter(
            student__user=self.request.user
        )

    def perform_update(self, serializer):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can update resumes."
            )

        resume = serializer.save()

        if resume.is_active:

            Resume.objects.filter(
                student=resume.student
            ).exclude(
                id=resume.id
            ).update(
                is_active=False
            )

        resume.student.update_profile_completion()

    def perform_destroy(self, instance):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can delete resumes."
            )

        student = instance.student

        instance.delete()

        student.update_profile_completion()


# ============================================================
# ACTIVATE RESUME
# ============================================================
@extend_schema(tags=["Students"])
class ResumeActivateView(
    generics.UpdateAPIView
):

    serializer_class = ResumeSerializer

    def get_queryset(self):

        return Resume.objects.filter(
            student__user=self.request.user
        )

    def update(self, request, *args, **kwargs):

        if request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can activate a resume."
            )

        resume = self.get_object()

        Resume.objects.filter(
            student=resume.student
        ).update(
            is_active=False
        )

        resume.is_active = True

        resume.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        resume.student.update_profile_completion()

        serializer = self.get_serializer(
            resume
        )

        return Response(
            serializer.data
        )




#Student DashboardView
@extend_schema(tags=["Students"])
class StudentDashboardView(generics.RetrieveAPIView):

    serializer_class = StudentDashboardSerializer

    def get_object(self):

        if self.request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can access the student dashboard."
            )

        try:
            profile = (
                StudentProfile.objects
                .select_related("user")
                .prefetch_related(
                    "education",
                    "projects",
                    "experience",
                    "resumes",
                    "user__skills__skill",
                )
                .get(
                    user=self.request.user
                )
            )

        except StudentProfile.DoesNotExist:

            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Create your student profile first."
            )

        return profile

    def retrieve(self, request, *args, **kwargs):

        profile = self.get_object()

        # Always ensure the latest completion value.
        profile.update_profile_completion()

        serializer = self.get_serializer(profile)

        return Response({
            "profile": serializer.data["profile"],
            "profile_completion": profile.profile_completion,
            "education": serializer.data["education"],
            "skills": serializer.data["skills"],
            "projects": serializer.data["projects"],
            "experience": serializer.data["experience"],
            "resumes": serializer.data["resumes"],
            "active_resume": serializer.data["active_resume"],
        })


# ============================================================
# ADMIN / TPO STUDENT MANAGEMENT
# ============================================================
@extend_schema(tags=["Admin / TPO"])
class AdminStudentListView(generics.ListAPIView):

    serializer_class = StudentProfileSerializer

    def get_queryset(self):

        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only TPO/Admin users can view all students."
            )

        queryset = (
            StudentProfile.objects
            .select_related("user")
            .order_by("roll_number")
        )

        department = self.request.query_params.get(
            "department"
        )

        graduation_year = self.request.query_params.get(
            "graduation_year"
        )

        if department:
            queryset = queryset.filter(
                department__iexact=department
            )

        if graduation_year:
            queryset = queryset.filter(
                graduation_year=graduation_year
            )

        return queryset
