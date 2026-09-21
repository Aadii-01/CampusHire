from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class Company(models.Model):

    name = models.CharField(
        max_length=200,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    website = models.URLField(
        blank=True,
    )

    industry = models.CharField(
        max_length=100,
        blank=True,
    )

    location = models.CharField(
        max_length=150,
        blank=True,
    )

    company_size = models.CharField(
        max_length=50,
        blank=True,
    )

    logo = models.ImageField(
        upload_to="company_logos/",
        null=True,
        blank=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name


class RecruiterProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recruiter_profile",
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="recruiters",
    )

    designation = models.CharField(
        max_length=100,
        blank=True,
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
    )

    is_primary = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.user.email} - "
            f"{self.company.name}"
        )
