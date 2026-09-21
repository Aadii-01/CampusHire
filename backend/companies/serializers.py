from rest_framework import serializers

from .models import Company, RecruiterProfile


class CompanySerializer(serializers.ModelSerializer):

    recruiter_count = serializers.IntegerField(
        source="recruiters.count",
        read_only=True,
    )

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "description",
            "website",
            "industry",
            "location",
            "company_size",
            "logo",
            "is_verified",
            "recruiter_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "is_verified",
            "recruiter_count",
            "created_at",
            "updated_at",
        ]


class RecruiterProfileSerializer(
    serializers.ModelSerializer
):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
    )

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = RecruiterProfile
        fields = [
            "id",
            "user",
            "user_email",
            "company",
            "company_name",
            "designation",
            "phone",
            "is_primary",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "user_email",
            "company_name",
            "created_at",
            "updated_at",
        ]
