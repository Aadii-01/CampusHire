from django.utils import timezone
from rest_framework import serializers

from .models import Job, JobEligibility, JobRequiredSkill


class JobSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
    )

    recruiter_email = serializers.EmailField(
        source="recruiter.email",
        read_only=True,
    )

    class Meta:
        model = Job

        fields = [
            "id",
            "company",
            "company_name",
            "recruiter",
            "recruiter_email",
            "title",
            "description",
            "employment_type",
            "work_mode",
            "location",
            "salary_min",
            "salary_max",
            "application_deadline",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
	    "company",
            "company_name",
            "recruiter",
            "recruiter_email",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):

        salary_min = data.get("salary_min")
        salary_max = data.get("salary_max")
        deadline = data.get("application_deadline")

        if (
            salary_min is not None
            and salary_max is not None
            and salary_max < salary_min
        ):
            raise serializers.ValidationError(
                "Maximum salary cannot be less than minimum salary."
            )

        if deadline and deadline <= timezone.now():
            raise serializers.ValidationError(
                "Application deadline must be in the future."
            )

        return data


class JobEligibilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = JobEligibility

        fields = [
            "id",
            "job",
            "min_cgpa",
            "max_backlogs",
            "graduation_year",
            "allowed_departments",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "job",
            "created_at",
            "updated_at",
        ]

    def validate_min_cgpa(self, value):

        if value is not None and (
            value < 0 or value > 10
        ):
            raise serializers.ValidationError(
                "CGPA must be between 0 and 10."
            )

        return value

    def validate_allowed_departments(self, value):

	    if not isinstance(value, list):
	        raise serializers.ValidationError(
	            "Allowed departments must be a list."
	        )

	    return value


class JobRequiredSkillSerializer(serializers.ModelSerializer):

    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True,
    )

    class Meta:
        model = JobRequiredSkill

        fields = [
            "id",
            "job",
            "skill",
            "skill_name",
            "required_proficiency",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "job",
            "skill_name",
            "created_at",
        ]


