from django.urls import path

from .views import (
	StudentApplicationListCreateView, 
	StudentApplicationDetailView,
	RecruiterJobApplicationListView,
    AdminApplicationStatusUpdateView,
    AdminInterviewCreateView,
    StudentInterviewListView,
    RecruiterInterviewListView,
    AdminInterviewListView,
AdminInterviewUpdateView,
    AdminInterviewStatusUpdateView,
)


urlpatterns = [
    path(
        "",
        StudentApplicationListCreateView.as_view(),
        name="student-application-list-create",
    ),
   path(
    "<int:pk>/",
    StudentApplicationDetailView.as_view(),
    name="student-application-detail",
),
path(
    "job/<int:job_id>/",
    RecruiterJobApplicationListView.as_view(),
    name="recruiter-job-applications",
),
path(
    "<int:pk>/status/",
    AdminApplicationStatusUpdateView.as_view(),
    name="admin-application-status-update",
),
path(
    "interviews/",
    AdminInterviewCreateView.as_view(),
    name="admin-interview-create",
),
path(
    "interviews/",
    AdminInterviewCreateView.as_view(),
    name="admin-interview-create",
),
path(
    "interviews/student/",
    StudentInterviewListView.as_view(),
    name="student-interview-list",
),
path(
    "interviews/recruiter/",
    RecruiterInterviewListView.as_view(),
    name="recruiter-interview-list",
),
path(
    "interviews/admin/",
    AdminInterviewListView.as_view(),
    name="admin-interview-list",
),
path(
    "interviews/<int:pk>/",
    AdminInterviewUpdateView.as_view(),
    name="admin-interview-update",
),
path(
    "interviews/<int:pk>/status/",
    AdminInterviewStatusUpdateView.as_view(),
    name="admin-interview-status-update",
),

]
