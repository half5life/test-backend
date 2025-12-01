from django.db import models

class Role(models.Model):
    """
    Справочник ролей в системе.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Название роли (например: admin, manager, user)")
    description = models.TextField(blank=True, help_text="Описание роли")

    def __str__(self):
        return self.name
