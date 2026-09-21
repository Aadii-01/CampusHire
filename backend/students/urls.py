from django.urls import path

from .views import (
    StudentProfileCreateView,
    StudentProfileView,
    EducationListCreateView,
    EducationDetailView,
ProjectListCreateView,
ProjectDetailView,
ExperienceListCreateView,
ExperienceDetailView,
ResumeListCreateView,
ResumeDetailView,
ResumeActivateView,
StudentDashboardView,
)

urlpatterns = [
    path(
        "profile/",
        StudentProfileView.as_view(),
        name="student-profile",
    ),
    path(
        "profile/create/",
        StudentProfileCreateView.as_view(),
        name="student-profile-create",
    ),
path(
    "education/",
    EducationListCreateView.as_view(),
    name="education-list-create",
),

path(
    "education/<int:pk>/",
    EducationDetailView.as_view(),
    name="education-detail",
),

path(
    "projects/",
    ProjectListCreateView.as_view(),
    name="project-list-create",
),
path(
    "projects/<int:pk>/",
    ProjectDetailView.as_view(),
    name="project-detail",
),

path(
    "experience/",
    ExperienceListCreateView.as_view(),
    name="experience-list-create",
),

path(
    "experience/<int:pk>/",
    ExperienceDetailView.as_view(),
    name="experience-detail",
),
path(
    "resumes/",
    ResumeListCreateView.as_view(),
    name="resume-list-create",
),

path(
    "resumes/<int:pk>/",
    ResumeDetailView.as_view(),
    name="resume-detail",
),
path(
    "resumes/<int:pk>/activate/",
    ResumeActivateView.as_view(),
    name="resume-activate",
),
path(
    "dashboard/",
    StudentDashboardView.as_view(),
    name="student-dashboard",
),
]
