from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Viewsets için router kullanıyoruz
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'calls', views.CallRecordViewSet, basename='calls')
router.register(r'evaluations', views.EvaluationViewSet)
router.register(r'evaluation-forms', views.EvaluationFormViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # API görünümünde oturum açma/kapatma için DRF'nin standart görünümlerini kullanabiliriz
    path('auth/', include('rest_framework.urls')),
] 