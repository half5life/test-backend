from rest_framework.permissions import BasePermission
from .models import RolePermission

class RbacPermission(BasePermission):
    """
    Кастомный Permission Class для реализации RBAC.
    Проверяет права доступа пользователя к ресурсу на основе его роли.
    
    View, использующий этот permission, должен иметь атрибут `resource_name`.
    """

    def has_permission(self, request, view):
        # 1. Если пользователь не залогинен -> 401 Unauthorized (обычно обрабатывается IsAuthenticated, но проверим тут)
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Определяем запрашиваемый ресурс
        resource_name = getattr(view, 'resource_name', None)
        if not resource_name:
            # Если ресурс не указан во View, запрещаем доступ (безопасность по умолчанию)
            return False

        # Если у пользователя нет роли, считаем, что прав нет
        if not request.user.role:
            return False

        # 3. Ищем в БД запись RolePermission для текущей role пользователя и целевого resource
        try:
            permission = RolePermission.objects.get(
                role=request.user.role,
                resource__name=resource_name
            )
        except RolePermission.DoesNotExist:
            # 6. Если записи нет -> 403 Forbidden
            return False

        # 4-5. Проверяем соответствующий флаг в зависимости от метода
        method = request.method.upper()

        if method == 'GET':
            return permission.can_read
        elif method == 'POST':
            return permission.can_create
        elif method in ['PUT', 'PATCH']:
            return permission.can_update
        elif method == 'DELETE':
            return permission.can_delete
        
        # Поддержка HEAD как GET (опционально, но часто требуется)
        if method == 'HEAD':
            return permission.can_read

        # Для остальных методов запрещаем доступ
        return False
