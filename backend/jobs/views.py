from django.shortcuts import render
from drf_spectacular.utils import extend_schema
# Create your views here.
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from students.models import StudentProfile

from companies.models import RecruiterProfile

from django.shortcuts import get_object_or_404

from .models import Job, JobEligibility, JobRequiredSkill
from .serializers import(
 JobSerializer,     
JobEligibilitySerializer,
    JobRequiredSkillSerializer,
)

@extend_schema(tags=["Jobs"])
class JobListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = JobSerializer

    def get_queryset(self):

        return (
            Job.objects
            .select_related(
                "company",
                "recruiter",
            )
            .order_by("-created_at")
        )

    def perform_create(self, serializer):

        if self.request.user.role != "RECRUITER":
            raise PermissionDenied(
                "Only recruiters can create jobs."
            )

        try:
            recruiter_profile = (
                RecruiterProfile.objects
                .select_related("company")
                .get(
                    user=self.request.user
                )
            )

        except RecruiterProfile.DoesNotExist:

            raise PermissionDenied(
                "Create your recruiter profile first."
            )

        serializer.save(
            company=recruiter_profile.company,
            recruiter=self.request.user,
        )

@extend_schema(tags=["Admin / TPO"])
class AdminJobListView(
    generics.ListAPIView
):

    serializer_class = JobSerializer

    def get_queryset(self):

        if self.request.user.role != "ADMIN":
            raise PermissionDenied(
                "Only TPO/Admin users can view all jobs."
            )

        queryset = (
            Job.objects
            .select_related(
                "company",
                "recruiter",
            )
            .order_by("-created_at")
        )

        status = self.request.query_params.get(
            "status"
        )

        company_id = self.request.query_params.get(
            "company"
        )

        if status:
            queryset = queryset.filter(
                status=status
            )

        if company_id:
            queryset = queryset.filter(
                company_id=company_id
            )

        return queryset


@extend_schema(tags=["Jobs"])
class JobDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = JobSerializer

    def get_queryset(self):

        return Job.objects.select_related(
            "company",
            "recruiter",
        )

    def perform_update(self, serializer):

        if self.request.user.role != "RECRUITER":
            raise PermissionDenied(
                "Only recruiters can update jobs."
            )

        job = self.get_object()

        if job.recruiter != self.request.user:
            raise PermissionDenied(
                "You can only update your own jobs."
            )

        serializer.save(
            company=job.company,
            recruiter=job.recruiter,
        )

    def perform_destroy(self, instance):

        if self.request.user.role != "RECRUITER":
            raise PermissionDenied(
                "Only recruiters can delete jobs."
            )

        if instance.recruiter != self.request.user:
            raise PermissionDenied(
                "You can only delete your own jobs."
            )

        instance.delete()

@extend_schema(tags=["Jobs"])
class JobEligibilityView(
    generics.GenericAPIView
):

    serializer_class = JobEligibilitySerializer

    def get_job(self):

        return get_object_or_404(
            Job,
            pk=self.kwargs["job_id"],
        )

    def get_object(self):

        job = self.get_job()

        try:
            return JobEligibility.objects.get(
                job=job
            )

        except JobEligibility.DoesNotExist:

            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Eligibility criteria not configured for this job."
            )

    def check_recruiter_access(self, job):

        if self.request.user.role != "RECRUITER":
            raise PermissionDenied(
                "Only recruiters can manage job eligibility."
            )

        if job.recruiter != self.request.user:
            raise PermissionDenied(
                "You can only manage eligibility for your own jobs."
            )

    def get(self, request, *args, **kwargs):

        job = self.get_job()

        self.check_recruiter_access(job)

        eligibility = self.get_object()

        serializer = self.get_serializer(
            eligibility
        )

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):

        job = self.get_job()

        self.check_recruiter_access(job)

        if JobEligibility.objects.filter(
            job=job
        ).exists():

            raise PermissionDenied(
                "Eligibility criteria already exist for this job."
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save(
            job=job
        )

        return Response(
            serializer.data,
            status=201
        )

    def patch(self, request, *args, **kwargs):

        job = self.get_job()

        self.check_recruiter_access(job)

        eligibility = self.get_object()

        serializer = self.get_serializer(
            eligibility,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save(
            job=job
        )

        return Response(
            serializer.data
        )


@extend_schema(tags=["Jobs"])
class JobRequiredSkillListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = JobRequiredSkillSerializer

    def get_job(self):

        return get_object_or_404(
            Job,
            pk=self.kwargs["job_id"],
        )

    def get_queryset(self):

        job = self.get_job()

        return (
            JobRequiredSkill.objects
            .filter(job=job)
            .select_related("skill")
            .order_by("skill__name")
        )

    def perform_create(self, serializer):

        job = self.get_job()

        if self.request.user.role != "RECRUITER":
            raise PermissionDenied(
                "Only recruiters can manage required skills."
            )

        if job.recruiter != self.request.user:
            raise PermissionDenied(
                "You can only manage required skills for your own jobs."
            )

        serializer.save(
            job=job
        )


@extend_schema(tags=["Jobs"])
class JobRequiredSkillDetailView(
    generics.DestroyAPIView
):

    serializer_class = JobRequiredSkillSerializer

    def get_queryset(self):

        return JobRequiredSkill.objects.filter(
            job__recruiter=self.request.user
        )

    def perform_destroy(self, instance):

        if self.request.user.role != "RECRUITER":
            raise PermissionDenied(
                "Only recruiters can remove required skills."
            )

        if instance.job.recruiter != self.request.user:
            raise PermissionDenied(
                "You can only remove skills from your own jobs."
            )

        instance.delete()


@extend_schema(tags=["Jobs"], responses=dict)
class JobEligibilityCheckView(
    generics.GenericAPIView
):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        if request.user.role != "STUDENT":
            raise PermissionDenied(
                "Only students can check job eligibility."
            )

        job = get_object_or_404(
            Job,
            pk=kwargs["job_id"],
        )

        try:
            student = StudentProfile.objects.get(
                user=request.user
            )

        except StudentProfile.DoesNotExist:

            raise PermissionDenied(
                "Create your student profile first."
            )

        try:
            eligibility = JobEligibility.objects.get(
                job=job
            )

        except JobEligibility.DoesNotExist:

            return Response({
                "eligible": True,
                "message": "No eligibility criteria configured for this job.",
                "failed_criteria": [],
                "missing_skills": [],
            })

        failed_criteria = []
        missing_skills = []

        # --------------------------------
        # CGPA
        # --------------------------------

        if (
            eligibility.min_cgpa is not None
            and student.cgpa < eligibility.min_cgpa
        ):
            failed_criteria.append({
                "criterion": "CGPA",
                "required": str(
                    eligibility.min_cgpa
                ),
                "actual": str(
                    student.cgpa
                ),
            })

        # --------------------------------
        # Backlogs
        # --------------------------------

        if (
            eligibility.max_backlogs is not None
            and student.backlogs >
            eligibility.max_backlogs
        ):
            failed_criteria.append({
                "criterion": "Backlogs",
                "required": eligibility.max_backlogs,
                "actual": student.backlogs,
            })

        # --------------------------------
        # Graduation year
        # --------------------------------

        if (
            eligibility.graduation_year is not None
            and student.graduation_year !=
            eligibility.graduation_year
        ):
            failed_criteria.append({
                "criterion": "Graduation Year",
                "required": eligibility.graduation_year,
                "actual": student.graduation_year,
            })

        # --------------------------------
        # Department
        # --------------------------------

        allowed_departments = (
            eligibility.allowed_departments or []
        )

        if (
            allowed_departments
            and student.department
            not in allowed_departments
        ):
            failed_criteria.append({
                "criterion": "Department",
                "required": allowed_departments,
                "actual": student.department,
            })

        # --------------------------------
        # Student skills
        # --------------------------------

        student_skills = {
            student_skill.skill.name.lower(): student_skill
            for student_skill
            in request.user.skills.select_related(
                "skill"
            ).all()
        }

        proficiency_order = {
            "BEGINNER": 1,
            "INTERMEDIATE": 2,
            "ADVANCED": 3,
        }

        required_skills = (
            JobRequiredSkill.objects
            .filter(job=job)
            .select_related("skill")
        )

        for required_skill in required_skills:

            skill_name = (
                required_skill.skill.name.lower()
            )

            student_skill = student_skills.get(
                skill_name
            )

            if not student_skill:

                missing_skills.append({
                    "skill": required_skill.skill.name,
                    "required_proficiency":
                        required_skill.required_proficiency,
                    "actual_proficiency": None,
                })

                continue

            required_level = proficiency_order[
                required_skill.required_proficiency
            ]

            actual_level = proficiency_order[
                student_skill.proficiency
            ]

            if actual_level < required_level:

                missing_skills.append({
                    "skill": required_skill.skill.name,
                    "required_proficiency":
                        required_skill.required_proficiency,
                    "actual_proficiency":
                        student_skill.proficiency,
                })

        eligible = (
            len(failed_criteria) == 0
            and len(missing_skills) == 0
        )

        return Response({
            "job_id": job.id,
            "job_title": job.title,
            "eligible": eligible,
            "failed_criteria": failed_criteria,
            "missing_skills": missing_skills,
        })


