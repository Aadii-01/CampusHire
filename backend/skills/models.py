from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class Skill(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class StudentSkill(models.Model):

    class Proficiency(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skills",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="students",
    )

    proficiency = models.CharField(
        max_length=20,
        choices=Proficiency.choices,
        default=Proficiency.INTERMEDIATE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "skill"],
                name="unique_student_skill",
            )
        ]

    def __str__(self):
        return f"{self.student.email} - {self.skill.name}"
