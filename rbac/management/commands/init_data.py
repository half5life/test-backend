from django.core.management.base import BaseCommand
from users.models import Role
from rbac.models import Resource, RolePermission

class Command(BaseCommand):
    help = 'Инициализация начальных данных (Роли, Ресурсы, Права)'

    def handle(self, *args, **options):
        self.stdout.write('Создание ролей...')
        admin_role, _ = Role.objects.get_or_create(name='admin', defaults={'description': 'Администратор системы'})
        user_role, _ = Role.objects.get_or_create(name='user', defaults={'description': 'Обычный пользователь'})

        self.stdout.write('Создание ресурсов...')
        # Ресурс для финансовых отчетов (пример)
        res_reports, _ = Resource.objects.get_or_create(
            name='financial_reports', 
            defaults={'description': 'Финансовые отчеты'}
        )
        # Ресурс для списка пользователей
        res_users, _ = Resource.objects.get_or_create(
            name='users_list', 
            defaults={'description': 'Список пользователей'}
        )
        # Ресурс для настроек
        res_settings, _ = Resource.objects.get_or_create(
            name='settings', 
            defaults={'description': 'Системные настройки'}
        )

        self.stdout.write('Настройка прав доступа...')
        
        # 1. Админ имеет полный доступ ко всем ресурсам
        resources = [res_reports, res_users, res_settings]
        for res in resources:
            RolePermission.objects.update_or_create(
                role=admin_role,
                resource=res,
                defaults={
                    'can_create': True,
                    'can_read': True,
                    'can_update': True,
                    'can_delete': True
                }
            )

        # 2. Пользователь имеет доступ только на чтение отчетов
        RolePermission.objects.update_or_create(
            role=user_role,
            resource=res_reports,
            defaults={
                'can_create': False, # Не может создавать
                'can_read': True,    # Может читать
                'can_update': False, # Не может обновлять
                'can_delete': False  # Не может удалять
            }
        )

        # Для остальных ресурсов пользователю ничего не создаем -> доступ будет запрещен (403)

        self.stdout.write(self.style.SUCCESS('Данные успешно инициализированы'))
