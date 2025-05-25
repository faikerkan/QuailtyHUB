from django.urls import path

from . import views

app_name = "calls"

urlpatterns = [
    # Call management
    path("", views.call_list, name="call_list"),
    path("create/", views.call_create, name="call_create"),
    path("<int:call_id>/", views.call_detail, name="call_detail"),
    path("<int:call_id>/edit/", views.call_edit, name="call_edit"),
    path("<int:call_id>/delete/", views.call_delete, name="call_delete"),
    
    # Call evaluation
    path("<int:call_id>/evaluate/", views.call_evaluate, name="call_evaluate"),
    path("evaluations/", views.evaluation_list, name="evaluation_list"),
    path("evaluations/<int:evaluation_id>/", views.evaluation_detail, name="evaluation_detail"),
    
    # Reports and analytics
    path("reports/", views.reports, name="reports"),
    path("analytics/", views.analytics, name="analytics"),
]
