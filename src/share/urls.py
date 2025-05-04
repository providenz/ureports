from django.urls import path
from share import views

urlpatterns = [
    path("project/<slug:slug>/share/", views.share_project, name="share_project"),
    path(
        "project/<slug:slug>/revoke/<int:user_id>/",
        views.revoke_share,
        name="revoke_share",
    ),
    path(
        "sharing-projects/",
        views.list_projects_for_sharing,
        name="list_projects_for_sharing",
    ),
    path("ajax/email_search/", views.email_search_view, name="email_search_view"),
    path(
        "ajax/share_with_email/",
        views.share_with_email_view,
        name="share_with_email_view",
    ),
]
