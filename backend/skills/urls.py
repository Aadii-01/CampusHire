from django.urls import path

from .views import (
    SkillListCreateView,
    StudentSkillDeleteView,
    StudentSkillListCreateView,
)


urlpatterns = [
    path(
        "",
        SkillListCreateView.as_view(),
        name="skill-list-create",
    ),
    path(
        "my/",
        StudentSkillListCreateView.as_view(),
        name="student-skill-list-create",
    ),
    path(
        "my/<int:pk>/",
        StudentSkillDeleteView.as_view(),
        name="student-skill-delete",
    ),
]
