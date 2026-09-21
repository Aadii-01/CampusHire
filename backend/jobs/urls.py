from django.urls import path

from .views import (
    JobListCreateView,
    JobDetailView,
    JobEligibilityView,
    JobRequiredSkillListCreateView,
    JobRequiredSkillDetailView,
    JobEligibilityCheckView,
)


urlpatterns = [

    path(
        "",
        JobListCreateView.as_view(),
        name="job-list-create",
    ),

    path(
        "<int:pk>/",
        JobDetailView.as_view(),
        name="job-detail",
    ),

    path(
        "<int:job_id>/eligibility/",
        JobEligibilityView.as_view(),
        name="job-eligibility",
    ),

    path(
        "<int:job_id>/required-skills/",
        JobRequiredSkillListCreateView.as_view(),
        name="job-required-skills",
    ),

    path(
        "<int:job_id>/required-skills/<int:pk>/",
        JobRequiredSkillDetailView.as_view(),
        name="job-required-skill-detail",
    ),
path(
    "<int:job_id>/eligibility/check/",
    JobEligibilityCheckView.as_view(),
    name="job-eligibility-check",
),

]
