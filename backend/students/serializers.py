from rest_framework import serializers

from .models import (
	StudentProfile, 
	Education, 
	Project, 
	Experience, 
	Resume,
	
)


class StudentProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user",
            "roll_number",
            "phone",
            "date_of_birth",
            "gender",
            "department",
            "graduation_year",
            "cgpa",
            "backlogs",
            "bio",
            "profile_photo",
            "profile_completion",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "profile_completion",
            "created_at",
            "updated_at",
        ]


class EducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Education
        fields = [
            "id",
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "percentage",
            "cgpa",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):

        start_year = data.get("start_year")
        end_year = data.get("end_year")

        if end_year and end_year < start_year:
            raise serializers.ValidationError(
                "End year cannot be before start year."
            )

        if data.get("cgpa") is not None:
            if data["cgpa"] < 0 or data["cgpa"] > 10:
                raise serializers.ValidationError(
                    "CGPA must be between 0 and 10."
                )

        if data.get("percentage") is not None:
            if data["percentage"] < 0 or data["percentage"] > 100:
                raise serializers.ValidationError(
                    "Percentage must be between 0 and 100."
                )

        return data


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "technologies",
            "github_url",
            "live_url",
            "start_date",
            "end_date",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                "End date cannot be before start date."
            )

        return data


class ExperienceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Experience
        fields = [
            "id",
            "company_name",
            "job_title",
            "location",
            "employment_type",
            "start_date",
            "end_date",
            "description",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                "End date cannot be before start date."
            )

        return data



class ResumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resume
        fields = [
            "id",
            "title",
            "file",
            "version",
            "is_active",
            "file_size",
            "uploaded_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "version",
            "file_size",
            "uploaded_at",
            "updated_at",
        ]

    def validate_file(self, file):

        if not file.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Only PDF files are allowed."
            )

        max_size = 5 * 1024 * 1024

        if file.size > max_size:
            raise serializers.ValidationError(
                "Resume file size cannot exceed 5 MB."
            )

        return file

class StudentDashboardSerializer(serializers.Serializer):

    profile = serializers.SerializerMethodField()

    education = EducationSerializer(
        many=True
    )

    projects = ProjectSerializer(
        many=True
    )

    experience = ExperienceSerializer(
        many=True
    )

    resumes = ResumeSerializer(
        many=True
    )

    skills = serializers.SerializerMethodField()

    profile_completion = serializers.IntegerField()

    active_resume = serializers.SerializerMethodField()

    def get_profile(self, obj):

        return StudentProfileSerializer(obj).data

    def get_skills(self, obj):

        student = obj.user

        return [
            {
                "id": student_skill.id,
                "skill_id": student_skill.skill.id,
                "skill_name": student_skill.skill.name,
                "proficiency": student_skill.proficiency,
            }
            for student_skill in student.skills.select_related(
                "skill"
            ).all()
        ]

    def get_active_resume(self, obj):

        resume = obj.resumes.filter(
            is_active=True
        ).first()

        if not resume:
            return None

        return ResumeSerializer(resume).data
