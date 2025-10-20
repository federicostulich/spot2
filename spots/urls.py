from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpotViewSet
from .views import health 

router = DefaultRouter()
router.register(r"spots", SpotViewSet, basename="spot")

urlpatterns = [
    path("health/", health),
    path("", include(router.urls)),
]
