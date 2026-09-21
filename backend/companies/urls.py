from django.urls import path

from .views import (
    CompanyListCreateView,
    CompanyDetailView,
    RecruiterProfileCreateView,
    RecruiterProfileView,
)


urlpatterns = [

    # Companies
    path(
        "",
        CompanyListCreateView.as_view(),
        name="company-list-create",
    ),

    path(
        "<int:pk>/",
        CompanyDetailView.as_view(),
        name="company-detail",
    ),

    # Recruiter
    path(
        "recruiter/profile/create/",
        RecruiterProfileCreateView.as_view(),
        name="recruiter-profile-create",
    ),

    path(
        "recruiter/profile/",
        RecruiterProfileView.as_view(),
        name="recruiter-profile",
    ),
]
