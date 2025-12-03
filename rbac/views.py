from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Resource, RolePermission
from .serializers import ResourceSerializer, RolePermissionSerializer
from .permissions import RbacPermission

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (IsAuthenticated, RbacPermission)
    resource_name = 'resources'


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = (IsAuthenticated, RbacPermission)
    resource_name = 'permissions'