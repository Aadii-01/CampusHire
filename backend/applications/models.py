from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models

from jobs.models import Job


class Application(models.Model):

    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        INTERVIEW = "INTERVIEW", "Interview"
        SELECTED = "SELECTED", "Selected"
        REJECTED = "REJECTED", "Rejected"
        OFFERED = "OFFERED", "Offered"
        OFFER_ACCEPTED = "OFFER_ACCEPTED", "Offer Accepted"
        OFFER_DECLINED = "OFFER_DECLINED", "Offer Declined"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    resume = models.ForeignKey(
        "students.Resume",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
    )

    cover_letter = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.APPLIED,
    )

    applied_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "job"],
                name="unique_student_job_application",
            )
        ]
        ordering = ["-applied_at"]

    def __str__(self):
        return (
            f"{self.student.email} - "
            f"{self.job.title}"
        )


class Interview(models.Model):

    class InterviewType(models.TextChoices):
        ONLINE = "ONLINE", "Online"
        OFFLINE = "OFFLINE", "Offline"

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interviews",
    )

    round = models.CharField(max_length=100)

    interview_type = models.CharField(
        max_length=20,
        choices=InterviewType.choices,
        default=InterviewType.ONLINE,
    )

    scheduled_at = models.DateTimeField()

    location = models.CharField(
        max_length=255,
        blank=True,
    )

    meeting_link = models.URLField(
        blank=True,
    )

    interviewer = models.CharField(
        max_length=255,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )
		
    result = models.CharField(
	    max_length=30,
	    blank=True,	)

    feedback = models.TextField(
	    blank=True,
	)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"{self.application} - {self.round}"
