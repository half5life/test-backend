from django.db import models
from users.models import Role

class Resource(models.Model):
    """
    Справочник сущностей, к которым мы ограничиваем доступ.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Код ресурса (например: financial_reports)")
    description = models.TextField(blank=True, help_text="Описание ресурса")

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """
    Таблица, определяющая, что конкретная роль может делать с конкретным ресурсом.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='permissions')

    can_create = models.BooleanField(default=False, help_text="POST")
    can_read = models.BooleanField(default=False, help_text="GET")
    can_update = models.BooleanField(default=False, help_text="PUT/PATCH")
    can_delete = models.BooleanField(default=False, help_text="DELETE")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['role', 'resource'], name='unique_role_resource')
        ]
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'

    def __str__(self):
        return f"{self.role} -> {self.resource}"
