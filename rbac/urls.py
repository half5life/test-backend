from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourceViewSet, RolePermissionViewSet

router = DefaultRouter()
router.register(r'resources', ResourceViewSet)
router.register(r'permissions', RolePermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
