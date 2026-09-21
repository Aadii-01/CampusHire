from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


class StudentProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    roll_number = models.CharField(
        max_length=50,
        unique=True,
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )

    gender = models.CharField(
        max_length=20,
        blank=True,
    )

    department = models.CharField(
        max_length=100,
    )

    graduation_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(2000),
        ]
    )

    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    backlogs = models.PositiveIntegerField(
        default=0,
    )

    bio = models.TextField(
        blank=True,
    )

    profile_photo = models.ImageField(
        upload_to="student_profiles/",
        null=True,
        blank=True,
    )

    profile_completion = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.user.email} - {self.roll_number}"

    def calculate_profile_completion(self):

        completion = 0

        # ----------------------------------------------------
        # Basic profile - 20%
        # ----------------------------------------------------

        basic_fields = [
            self.phone,
            self.date_of_birth,
            self.gender,
            self.department,
            self.graduation_year,
            self.cgpa,
        ]

        if all(
            field not in [None, ""]
            for field in basic_fields
        ):
            completion += 20

        # ----------------------------------------------------
        # Education - 20%
        # ----------------------------------------------------

        if self.education.exists():
            completion += 20

        # ----------------------------------------------------
        # Skills - 15%
        # ----------------------------------------------------

        if self.user.skills.exists():
            completion += 15

        # ----------------------------------------------------
        # Projects - 15%
        # ----------------------------------------------------

        if self.projects.exists():
            completion += 15

        # ----------------------------------------------------
        # Experience - 10%
        # ----------------------------------------------------

        if self.experience.exists():
            completion += 10

        # ----------------------------------------------------
        # Active Resume - 20%
        # ----------------------------------------------------

        if self.resumes.filter(
            is_active=True
        ).exists():
            completion += 20

        return completion

    def update_profile_completion(self):

        self.profile_completion = (
            self.calculate_profile_completion()
        )

        self.save(
            update_fields=[
                "profile_completion",
                "updated_at",
            ]
        )


class Education(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="education",
    )

    institution = models.CharField(
        max_length=200,
    )

    degree = models.CharField(
        max_length=100,
    )

    field_of_study = models.CharField(
        max_length=100,
    )

    start_year = models.PositiveIntegerField()

    end_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.student.user.email} - {self.degree}"


class Project(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField()

    technologies = models.CharField(
        max_length=500,
        help_text="Comma-separated technologies used in the project.",
    )

    github_url = models.URLField(
        blank=True,
    )

    live_url = models.URLField(
        blank=True,
    )

    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.student.user.email} - {self.title}"


class Experience(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="experience",
    )

    company_name = models.CharField(
        max_length=200,
    )

    job_title = models.CharField(
        max_length=150,
    )

    location = models.CharField(
        max_length=150,
        blank=True,
    )

    employment_type = models.CharField(
        max_length=50,
        blank=True,
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.student.user.email} - {self.company_name}"


class Resume(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="resumes",
    )

    title = models.CharField(
        max_length=150,
        default="Resume",
    )

    file = models.FileField(
        upload_to="resumes/",
    )

    version = models.PositiveIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=False,
    )

    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.student.user.email} - "
            f"{self.title} v{self.version}"
        )
