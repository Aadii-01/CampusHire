from rest_framework import serializers

from applications.models import Application, Interview, Offer


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "resume",
            "cover_letter",
            "status",
            "applied_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "applied_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        job = attrs["job"]

        # 1. Role validation
        if user.role != "STUDENT":
            raise serializers.ValidationError(
                "Only students can apply for jobs."
            )

        # 2. Job status validation
        if job.status != "OPEN":
            raise serializers.ValidationError(
                "Applications are only allowed for open jobs."
            )

        # 3. Deadline validation
        from django.utils import timezone

        if job.application_deadline <= timezone.now():
            raise serializers.ValidationError(
                "The application deadline has passed."
            )

        # 4. Student profile validation
        try:
            profile = user.student_profile
        except Exception:
            raise serializers.ValidationError(
                "Please create your student profile before applying."
            )

        # 5. Active resume validation
        active_resume = profile.resumes.filter(
            is_active=True
        ).first()

        if not active_resume:
            raise serializers.ValidationError(
                "Please upload and activate a resume before applying."
            )

        # If the student doesn't explicitly provide a resume,
        # automatically use the active resume.
        if "resume" not in attrs:
            attrs["resume"] = active_resume

        # 6. Resume ownership validation
        resume = attrs["resume"]

        if resume.student.user != user:
            raise serializers.ValidationError(
                "You can only apply using your own resume."
            )

        if not resume.is_active:
            raise serializers.ValidationError(
                "Only your active resume can be submitted."
            )

        # 7. Eligibility validation
        from jobs.models import JobEligibility

        eligibility = JobEligibility.objects.filter(
            job=job
        ).first()

        if eligibility:
            failed_criteria = []

            if (
                eligibility.min_cgpa is not None
                and (
                    profile.cgpa is None
                    or profile.cgpa < eligibility.min_cgpa
                )
            ):
                failed_criteria.append(
                    "Minimum CGPA requirement not met."
                )

            if (
                eligibility.max_backlogs is not None
                and profile.backlogs > eligibility.max_backlogs
            ):
                failed_criteria.append(
                    "Maximum backlog requirement not met."
                )

            if (
                eligibility.graduation_year is not None
                and profile.graduation_year != eligibility.graduation_year
            ):
                failed_criteria.append(
                    "Graduation year requirement not met."
                )

            if eligibility.allowed_departments:
                if profile.department not in eligibility.allowed_departments:
                    failed_criteria.append(
                        "Department requirement not met."
                    )

            # Required skills
            proficiency_order = {
                "BEGINNER": 1,
                "INTERMEDIATE": 2,
                "ADVANCED": 3,
            }

            student_skills = {
                student_skill.skill.name.lower(): student_skill.proficiency
                for student_skill in user.skills.select_related("skill").all()
            }

            for required_skill in job.required_skills.select_related(
                "skill"
            ).all():
                skill_name = required_skill.skill.name.lower()

                if skill_name not in student_skills:
                    failed_criteria.append(
                        f"Missing required skill: "
                        f"{required_skill.skill.name}."
                    )
                    continue

                student_level = proficiency_order[
                    student_skills[skill_name]
                ]

                required_level = proficiency_order[
                    required_skill.required_proficiency
                ]

                if student_level < required_level:
                    failed_criteria.append(
                        f"Insufficient proficiency in "
                        f"{required_skill.skill.name}."
                    )

            if failed_criteria:
                raise serializers.ValidationError({
                    "eligibility": failed_criteria
                })

        # 8. Duplicate application validation
        if Application.objects.filter(
            student=user,
            job=job
        ).exists():
            raise serializers.ValidationError(
                "You have already applied for this job."
            )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]

        return Application.objects.create(
            student=request.user,
            **validated_data
        )


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "status",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "updated_at",
        ]

    def validate_status(self, value):
        application = self.instance

        allowed_transitions = {
            Application.Status.APPLIED: {
                Application.Status.UNDER_REVIEW,
                Application.Status.REJECTED,
            },
            Application.Status.UNDER_REVIEW: {
                Application.Status.SHORTLISTED,
                Application.Status.REJECTED,
            },
            Application.Status.SHORTLISTED: {
                Application.Status.INTERVIEW,
                Application.Status.REJECTED,
            },
            Application.Status.INTERVIEW: {
                Application.Status.SELECTED,
                Application.Status.REJECTED,
            },
            Application.Status.SELECTED: {
                Application.Status.OFFERED,
            },
            Application.Status.OFFERED: {
                Application.Status.OFFER_ACCEPTED,
                Application.Status.OFFER_DECLINED,
            },
            Application.Status.REJECTED: set(),
            Application.Status.OFFER_ACCEPTED: set(),
            Application.Status.OFFER_DECLINED: set(),
        }

        current_status = application.status

        if value == current_status:
            raise serializers.ValidationError(
                "Application is already in this status."
            )

        if value not in allowed_transitions.get(current_status, set()):
            raise serializers.ValidationError(
                f"Cannot change application status from "
                f"{current_status} to {value}."
            )

        return value


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = [
            "id",
            "application",
            "round",
            "interview_type",
            "scheduled_at",
            "location",
            "meeting_link",
            "interviewer",
            "notes",
            "result",
            "feedback",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        from django.utils import timezone

        # Creation: application must be shortlisted
        if self.instance is None:
            application = attrs["application"]

            if application.status != Application.Status.SHORTLISTED:
                raise serializers.ValidationError(
                    "Interviews can only be scheduled for "
                    "shortlisted applications."
                )

        # If scheduled_at is being changed, it must remain in the future
        if "scheduled_at" in attrs:
            if attrs["scheduled_at"] <= timezone.now():
                raise serializers.ValidationError(
                    "Interview must be scheduled for a future date and time."
                )

        interview_type = attrs.get(
            "interview_type",
            getattr(
                self.instance,
                "interview_type",
                Interview.InterviewType.ONLINE,
            ),
        )

        meeting_link = attrs.get(
            "meeting_link",
            getattr(self.instance, "meeting_link", ""),
        )

        location = attrs.get(
            "location",
            getattr(self.instance, "location", ""),
        )

        if (
            interview_type == Interview.InterviewType.ONLINE
            and not meeting_link
        ):
            raise serializers.ValidationError(
                {
                    "meeting_link": (
                        "Meeting link is required for online interviews."
                    )
                }
            )

        if (
            interview_type == Interview.InterviewType.OFFLINE
            and not location
        ):
            raise serializers.ValidationError(
                {
                    "location": (
                        "Location is required for offline interviews."
                    )
                }
            )

        # Results can only be recorded for completed interviews
        if "result" in attrs or "feedback" in attrs:
            current_status = (
                self.instance.status
                if self.instance is not None
                else Interview.Status.SCHEDULED
            )

            if current_status != Interview.Status.COMPLETED:
                raise serializers.ValidationError(
                    "Interview result and feedback can only be recorded "
                    "after the interview is completed."
                )

        if "result" in attrs:
            allowed_results = {
                "PASS",
                "FAIL",
                "ON_HOLD",
            }

            if attrs["result"] not in allowed_results:
                raise serializers.ValidationError(
                    {
                        "result": (
                            "Result must be one of: PASS, FAIL, ON_HOLD."
                        )
                    }
                )

        return attrs


class InterviewStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = [
            "id",
            "status",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "updated_at",
        ]

    def validate_status(self, value):
        interview = self.instance

        allowed_transitions = {
            Interview.Status.SCHEDULED: {
                Interview.Status.COMPLETED,
                Interview.Status.CANCELLED,
            },
            Interview.Status.COMPLETED: set(),
            Interview.Status.CANCELLED: set(),
        }

        current_status = interview.status

        if value == current_status:
            raise serializers.ValidationError(
                "Interview is already in this status."
            )

        if value not in allowed_transitions.get(current_status, set()):
            raise serializers.ValidationError(
                f"Cannot change interview status from "
                f"{current_status} to {value}."
            )

        return value


class OfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = [
            "id",
            "application",
            "designation",
            "ctc",
            "joining_date",
            "offer_expiry_date",
            "employment_type",
            "location",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        application = attrs["application"]

        if application.status != Application.Status.SELECTED:
            raise serializers.ValidationError(
                "An offer can only be created for a selected application."
            )

        if hasattr(application, "offer"):
            raise serializers.ValidationError(
                "An offer already exists for this application."
            )

        if attrs["offer_expiry_date"] < attrs["joining_date"]:
            raise serializers.ValidationError(
                "Offer expiry date cannot be before the joining date."
            )

        if attrs["ctc"] <= 0:
            raise serializers.ValidationError(
                "CTC must be greater than zero."
            )

        return attrs
