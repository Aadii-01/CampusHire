from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from companies.models import Company


class Job(models.Model):

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        INTERNSHIP = "INTERNSHIP", "Internship"

    class WorkMode(models.TextChoices):
        ONSITE = "ONSITE", "Onsite"
        HYBRID = "HYBRID", "Hybrid"
        REMOTE = "REMOTE", "Remote"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jobs_created",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField()

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
    )

    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
    )

    location = models.CharField(
        max_length=150,
        blank=True,
    )

    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    application_deadline = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.title} - {self.company.name}"


class JobEligibility(models.Model):

    job = models.OneToOneField(
        Job,
        on_delete=models.CASCADE,
        related_name="eligibility",
    )

    min_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    max_backlogs = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    allowed_departments = models.JSONField(
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Eligibility - {self.job.title}"


class JobRequiredSkill(models.Model):

    class RequiredProficiency(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="required_skills",
    )

    skill = models.ForeignKey(
        "skills.Skill",
        on_delete=models.CASCADE,
        related_name="job_requirements",
    )

    required_proficiency = models.CharField(
        max_length=20,
        choices=RequiredProficiency.choices,
        default=RequiredProficiency.INTERMEDIATE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "skill"],
                name="unique_job_required_skill",
            )
        ]

    def __str__(self):
        return (
            f"{self.job.title} - "
            f"{self.skill.name}"
        )



