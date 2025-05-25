from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("expert/", views.expert_dashboard, name="expert_dashboard"),
    path("agent/", views.agent_dashboard, name="agent_dashboard"),
    path("raporlar/", views.admin_reports, name="admin_reports"),
]
