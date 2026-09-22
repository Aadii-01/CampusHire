from django.test import TestCase

# Create your tests here.
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from companies.models import Company, RecruiterProfile
from jobs.models import Job, JobEligibility, JobRequiredSkill
from skills.models import Skill, StudentSkill
from students.models import StudentProfile, Resume

from .models import Application, Interview, Offer

User = get_user_model()


class ApplicationWorkflowTests(APITestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            email="applicationstudent@campushire.com",
            password="Student@123",
            role="STUDENT",
        )

        self.recruiter = User.objects.create_user(
            email="applicationrecruiter@campushire.com",
            password="Recruiter@123",
            role="RECRUITER",
        )

        self.company = Company.objects.create(
            name="Application Test Company",
            description="Company for application workflow tests.",
            website="https://www.applicationtest.com",
            industry="Information Technology",
            location="Bengaluru, India",
            company_size="51-200",
        )

        RecruiterProfile.objects.create(
            user=self.recruiter,
            company=self.company,
            designation="Campus Recruitment Manager",
            phone="9876543210",
            is_primary=True,
        )

        self.student_profile = StudentProfile.objects.create(
            user=self.student,
            roll_number="APPTEST001",
            phone="9876543211",
            date_of_birth="2003-01-15",
            gender="Male",
            department="Information Technology",
            graduation_year=2027,
            cgpa=7.01,
            backlogs=0,
            bio="Application workflow test student.",
        )

        self.python = Skill.objects.create(name="Python")
        self.django = Skill.objects.create(name="Django")

        StudentSkill.objects.create(
            student=self.student,
            skill=self.python,
            proficiency="INTERMEDIATE",
        )

        StudentSkill.objects.create(
            student=self.student,
            skill=self.django,
            proficiency="INTERMEDIATE",
        )

        self.job = Job.objects.create(
            company=self.company,
            recruiter=self.recruiter,
            title="Application Test Engineer",
            description="Job for application workflow tests.",
            employment_type="FULL_TIME",
            work_mode="ONSITE",
            location="Bengaluru, India",
            salary_min=600000,
            salary_max=900000,
            application_deadline=timezone.now() + timedelta(days=30),
            status="OPEN",
        )

        JobEligibility.objects.create(
            job=self.job,
            min_cgpa=6.50,
            max_backlogs=2,
            graduation_year=2027,
            allowed_departments=[
                "Information Technology",
                "Computer Science",
            ],
        )

        JobRequiredSkill.objects.create(
            job=self.job,
            skill=self.python,
            required_proficiency="INTERMEDIATE",
        )

        JobRequiredSkill.objects.create(
            job=self.job,
            skill=self.django,
            required_proficiency="INTERMEDIATE",
        )

        self.resume = Resume.objects.create(
            student=self.student_profile,
            version=1,
            file="resumes/test_resume.pdf",
            is_active=True,
        )

        self.application_url = reverse(
            "student-application-list-create"
        )

    def authenticate_student(self):
        self.client.force_authenticate(user=self.student)

    def authenticate_recruiter(self):
        self.client.force_authenticate(user=self.recruiter)

    def create_application(self):
        self.authenticate_student()

        response = self.client.post(
            self.application_url,
            {
                "job": self.job.id,
                "resume": self.resume.id,
                "cover_letter": "I am interested in this campus opportunity.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        return Application.objects.get(
            student=self.student,
            job=self.job,
        )

    def test_student_can_apply_to_eligible_open_job(self):
        self.authenticate_student()

        response = self.client.post(
            self.application_url,
            {
                "job": self.job.id,
                "resume": self.resume.id,
                "cover_letter": "I am interested in this campus opportunity.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        application = Application.objects.get(
            student=self.student,
            job=self.job,
        )

        self.assertEqual(
            application.status,
            Application.Status.APPLIED,
        )

    def test_student_cannot_apply_twice_to_same_job(self):
        self.create_application()

        self.authenticate_student()

        response = self.client.post(
            self.application_url,
            {
                "job": self.job.id,
                "resume": self.resume.id,
                "cover_letter": "Second application attempt.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_ineligible_student_cannot_apply(self):
        self.student_profile.cgpa = 5.50
        self.student_profile.save()

        self.authenticate_student()

        response = self.client.post(
            self.application_url,
            {
                "job": self.job.id,
                "resume": self.resume.id,
                "cover_letter": "Application with insufficient CGPA.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_recruiter_cannot_apply(self):
        self.authenticate_recruiter()

        response = self.client.post(
            self.application_url,
            {
                "job": self.job.id,
                "resume": self.resume.id,
                "cover_letter": "Recruiter application attempt.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_application_status_transition_is_enforced(self):
        application = self.create_application()

        admin = User.objects.create_user(
            email="applicationadmin@campushire.com",
            password="Admin@123",
            role="ADMIN",
        )

        self.client.force_authenticate(user=admin)

        status_url = reverse(
            "admin-application-status-update",
            kwargs={"pk": application.id},
        )

        response = self.client.patch(
            status_url,
            {"status": Application.Status.SELECTED},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_valid_application_status_transition(self):
        application = self.create_application()

        admin = User.objects.create_user(
            email="applicationadmin2@campushire.com",
            password="Admin@123",
            role="ADMIN",
        )

        self.client.force_authenticate(user=admin)

        status_url = reverse(
            "admin-application-status-update",
            kwargs={"pk": application.id},
        )

        response = self.client.patch(
            status_url,
            {"status": Application.Status.UNDER_REVIEW},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.UNDER_REVIEW,
        )


class InterviewWorkflowTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            email="interviewadmin@campushire.com",
            password="Admin@123",
            role="ADMIN",
        )

        self.student = User.objects.create_user(
            email="interviewstudent@campushire.com",
            password="Student@123",
            role="STUDENT",
        )

        self.recruiter = User.objects.create_user(
            email="interviewrecruiter@campushire.com",
            password="Recruiter@123",
            role="RECRUITER",
        )

        self.company = Company.objects.create(
            name="Interview Test Company",
            description="Company for interview tests.",
            website="https://www.interviewtest.com",
            industry="Information Technology",
            location="Bengaluru, India",
            company_size="51-200",
        )

        RecruiterProfile.objects.create(
            user=self.recruiter,
            company=self.company,
            designation="Recruitment Manager",
            phone="9876543210",
            is_primary=True,
        )

        student_profile = StudentProfile.objects.create(
            user=self.student,
            roll_number="INTTEST001",
            phone="9876543211",
            date_of_birth="2003-01-15",
            gender="Male",
            department="Information Technology",
            graduation_year=2027,
            cgpa=7.01,
            backlogs=0,
            bio="Interview test student.",
        )

        skill_python = Skill.objects.create(
            name="Python"
        )

        skill_django = Skill.objects.create(
            name="Django"
        )

        StudentSkill.objects.create(
            student=self.student,
            skill=skill_python,
            proficiency="INTERMEDIATE",
        )

        StudentSkill.objects.create(
            student=self.student,
            skill=skill_django,
            proficiency="INTERMEDIATE",
        )

        job = Job.objects.create(
            company=self.company,
            recruiter=self.recruiter,
            title="Interview Test Engineer",
            description="Job for interview tests.",
            employment_type="FULL_TIME",
            work_mode="ONSITE",
            location="Bengaluru, India",
            salary_min=600000,
            salary_max=900000,
            application_deadline=timezone.now() + timedelta(days=30),
            status="OPEN",
        )

        JobEligibility.objects.create(
            job=job,
            min_cgpa=6.50,
            max_backlogs=2,
            graduation_year=2027,
            allowed_departments=[
                "Information Technology",
                "Computer Science",
            ],
        )

        JobRequiredSkill.objects.create(
            job=job,
            skill=skill_python,
            required_proficiency="INTERMEDIATE",
        )

        JobRequiredSkill.objects.create(
            job=job,
            skill=skill_django,
            required_proficiency="INTERMEDIATE",
        )

        resume = Resume.objects.create(
            student=student_profile,
            version=1,
            file="resumes/interview_test_resume.pdf",
            is_active=True,
        )

        self.application = Application.objects.create(
            student=self.student,
            job=job,
            resume=resume,
            cover_letter="Interview test application.",
            status=Application.Status.SHORTLISTED,
        )

        self.create_url = reverse(
            "admin-interview-create"
        )

        self.student_list_url = reverse(
            "student-interview-list"
        )

        self.recruiter_list_url = reverse(
            "recruiter-interview-list"
        )

        self.admin_list_url = reverse(
            "admin-interview-list"
        )

    def future_datetime(self):
        return (
            timezone.now() + timedelta(days=2)
        ).isoformat()

    def interview_payload(self):
        return {
            "application": self.application.id,
            "round": "Technical Interview",
            "interview_type": Interview.InterviewType.ONLINE,
            "scheduled_at": self.future_datetime(),
            "meeting_link": "https://meet.example.com/campushire",
            "interviewer": "Technical Interview Panel",
            "notes": "Technical round.",
        }

    def test_admin_can_schedule_online_interview(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.create_url,
            self.interview_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        interview = Interview.objects.get(
            application=self.application
        )

        self.assertEqual(
            interview.status,
            Interview.Status.SCHEDULED,
        )

        self.application.refresh_from_db()

        self.assertEqual(
            self.application.status,
            Application.Status.INTERVIEW,
        )

    def test_non_admin_cannot_schedule_interview(self):
        self.client.force_authenticate(
            user=self.recruiter
        )

        response = self.client.post(
            self.create_url,
            self.interview_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_online_interview_requires_meeting_link(self):
        self.client.force_authenticate(
            user=self.admin
        )

        payload = self.interview_payload()
        payload.pop("meeting_link")

        response = self.client.post(
            self.create_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_offline_interview_requires_location(self):
        self.client.force_authenticate(
            user=self.admin
        )

        payload = self.interview_payload()

        payload["interview_type"] = (
            Interview.InterviewType.OFFLINE
        )
        payload.pop("meeting_link")

        response = self.client.post(
            self.create_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_interview_must_be_scheduled_in_future(self):
        self.client.force_authenticate(
            user=self.admin
        )

        payload = self.interview_payload()

        payload["scheduled_at"] = (
            timezone.now() - timedelta(hours=1)
        ).isoformat()

        response = self.client.post(
            self.create_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_interview_cannot_be_created_for_non_shortlisted_application(self):
        self.application.status = (
            Application.Status.APPLIED
        )
        self.application.save()

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.create_url,
            self.interview_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_admin_can_complete_interview(self):
        self.client.force_authenticate(
            user=self.admin
        )

        create_response = self.client.post(
            self.create_url,
            self.interview_payload(),
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        interview_id = create_response.data["id"]

        status_url = reverse(
            "admin-interview-status-update",
            kwargs={"pk": interview_id},
        )

        response = self.client.patch(
            status_url,
            {
                "status": Interview.Status.COMPLETED
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        interview = Interview.objects.get(
            id=interview_id
        )

        self.assertEqual(
            interview.status,
            Interview.Status.COMPLETED,
        )

    def test_completed_interview_cannot_return_to_scheduled(self):
        self.client.force_authenticate(
            user=self.admin
        )

        create_response = self.client.post(
            self.create_url,
            self.interview_payload(),
            format="json",
        )

        interview_id = create_response.data["id"]

        status_url = reverse(
            "admin-interview-status-update",
            kwargs={"pk": interview_id},
        )

        self.client.patch(
            status_url,
            {
                "status": Interview.Status.COMPLETED
            },
            format="json",
        )

        response = self.client.patch(
            status_url,
            {
                "status": Interview.Status.SCHEDULED
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_interview_result_requires_completed_status(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.create_url,
            {
                **self.interview_payload(),
                "result": "PASS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_student_can_view_own_interviews(self):
        self.client.force_authenticate(
            user=self.admin
        )

        create_response = self.client.post(
            self.create_url,
            self.interview_payload(),
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(
            user=self.student
        )

        response = self.client.get(
            self.student_list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_recruiter_can_view_job_interviews(self):
        self.client.force_authenticate(
            user=self.admin
        )

        create_response = self.client.post(
            self.create_url,
            self.interview_payload(),
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.client.force_authenticate(
            user=self.recruiter
        )

        response = self.client.get(
            self.recruiter_list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )


class OfferWorkflowTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            email="offeradmin@campushire.com",
            password="Admin@123",
            role="ADMIN",
        )

        self.student = User.objects.create_user(
            email="offerstudent@campushire.com",
            password="Student@123",
            role="STUDENT",
        )

        self.recruiter = User.objects.create_user(
            email="offerrecruiter@campushire.com",
            password="Recruiter@123",
            role="RECRUITER",
        )

        company = Company.objects.create(
            name="Offer Test Company",
            description="Company for offer tests.",
            website="https://www.offertest.com",
            industry="Information Technology",
            location="Bengaluru, India",
            company_size="51-200",
        )

        RecruiterProfile.objects.create(
            user=self.recruiter,
            company=company,
            designation="Recruitment Manager",
            phone="9876543210",
            is_primary=True,
        )

        student_profile = StudentProfile.objects.create(
            user=self.student,
            roll_number="OFFERTEST001",
            phone="9876543211",
            date_of_birth="2003-01-15",
            gender="Male",
            department="Information Technology",
            graduation_year=2027,
            cgpa=7.01,
            backlogs=0,
            bio="Offer test student.",
        )

        resume = Resume.objects.create(
            student=student_profile,
            version=1,
            file="resumes/offer_test_resume.pdf",
            is_active=True,
        )

        job = Job.objects.create(
            company=company,
            recruiter=self.recruiter,
            title="Offer Test Engineer",
            description="Job for offer tests.",
            employment_type="FULL_TIME",
            work_mode="ONSITE",
            location="Bengaluru, India",
            salary_min=600000,
            salary_max=900000,
            application_deadline=timezone.now() + timedelta(days=30),
            status="OPEN",
        )

        self.application = Application.objects.create(
            student=self.student,
            job=job,
            resume=resume,
            cover_letter="Offer test application.",
            status=Application.Status.SELECTED,
        )

        self.create_url = reverse(
            "admin-offer-create"
        )

    def offer_payload(self):
        return {
            "application": self.application.id,
            "designation": "Software Engineer",
            "ctc": "800000.00",
            "joining_date": "2027-07-01",
            "offer_expiry_date": "2027-12-15",
            "employment_type": Offer.EmploymentType.FULL_TIME,
            "location": "Bengaluru, India",
            "notes": "Campus recruitment offer.",
        }

    def test_admin_can_create_offer_for_selected_application(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.create_url,
            self.offer_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        offer = Offer.objects.get(
            application=self.application
        )

        self.assertEqual(
            offer.designation,
            "Software Engineer",
        )

        self.application.refresh_from_db()

        self.assertEqual(
            self.application.status,
            Application.Status.OFFERED,
        )

    def test_non_admin_cannot_create_offer(self):
        self.client.force_authenticate(
            user=self.recruiter
        )

        response = self.client.post(
            self.create_url,
            self.offer_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_offer_requires_selected_application(self):
        self.application.status = (
            Application.Status.INTERVIEW
        )
        self.application.save()

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            self.create_url,
            self.offer_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_offer_expiry_cannot_be_before_joining_date(self):
        self.client.force_authenticate(
            user=self.admin
        )

        payload = self.offer_payload()

        payload["joining_date"] = "2027-12-15"
        payload["offer_expiry_date"] = "2027-07-01"

        response = self.client.post(
            self.create_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_offer_ctc_must_be_positive(self):
        self.client.force_authenticate(
            user=self.admin
        )

        payload = self.offer_payload()
        payload["ctc"] = "0"

        response = self.client.post(
            self.create_url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_duplicate_offer_is_rejected(self):
        self.client.force_authenticate(
            user=self.admin
        )

        first_response = self.client.post(
            self.create_url,
            self.offer_payload(),
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        # Creating another offer is also blocked by
        # the application status becoming OFFERED.
        response = self.client.post(
            self.create_url,
            self.offer_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
