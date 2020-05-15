from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tinychain import views


router = DefaultRouter()
router.register('alerts', views.AlertViewSet)

app_name = 'tinychain'

urlpatterns = [
    path('', include(router.urls))
]