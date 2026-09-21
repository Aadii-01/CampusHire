from rest_framework import serializers

from .models import Skill, StudentSkill


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class StudentSkillSerializer(serializers.ModelSerializer):

    skill_name = serializers.CharField(
        source="skill.name",
        read_only=True,
    )

    class Meta:
        model = StudentSkill
        fields = [
            "id",
            "skill",
            "skill_name",
            "proficiency",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]
