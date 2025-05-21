from django.urls import path
from . import views

app_name = 'calls'

urlpatterns = [
    path('', views.call_list, name='call_list'),
    path('<int:call_id>/', views.call_detail, name='call_detail'),
    path('upload/', views.call_upload, name='call_upload'),
    path('<int:call_id>/evaluate/', views.evaluate, name='evaluate'),
    path('evaluation/<int:evaluation_id>/', views.evaluation_detail, name='evaluation_detail'),
    path('my-evaluations/', views.my_evaluations, name='my_evaluations'),
] 