from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.models import Role
from rbac.models import Resource, RolePermission

User = get_user_model()

class Command(BaseCommand):
    help = 'Runs automated scenarios to test RBAC permissions'

    def handle(self, *args, **options):
        self.stdout.write('Setting up test data...')
        
        # 1. Ensure Roles and Resources exist (in case init_data wasn't run)
        admin_role, _ = Role.objects.get_or_create(name='admin')
        user_role, _ = Role.objects.get_or_create(name='user')
        
        res_reports, _ = Resource.objects.get_or_create(name='financial_reports')
        
        # 2. Setup Permissions
        # Admin: Full access
        RolePermission.objects.update_or_create(
            role=admin_role, resource=res_reports,
            defaults={'can_create': True, 'can_read': True, 'can_update': True, 'can_delete': True}
        )
        # User: Read-only
        RolePermission.objects.update_or_create(
            role=user_role, resource=res_reports,
            defaults={'can_create': False, 'can_read': True, 'can_update': False, 'can_delete': False}
        )

        # 3. Create Test Users
        admin_user, _ = User.objects.get_or_create(email='admin_test@example.com')
        admin_user.set_password('pass123')
        admin_user.role = admin_role
        admin_user.save()

        simple_user, _ = User.objects.get_or_create(email='user_test@example.com')
        simple_user.set_password('pass123')
        simple_user.role = user_role
        simple_user.save()

        client = APIClient()
        url = '/api/reports/'

        self.stdout.write(self.style.WARNING('\n--- STARTING SCENARIOS ---\n'))

        # SCENARIO 1: Anonymous Access
        self.stdout.write('1. Anonymous Access (GET)... ', ending='')
        response = client.get(url)
        if response.status_code == 401:
            self.stdout.write(self.style.SUCCESS('OK (401 Unauthorized)'))
        else:
            self.stdout.write(self.style.ERROR(f'FAIL (Got {response.status_code})'))

        # SCENARIO 2: User Access (GET) -> Should be allowed
        self.stdout.write('2. User Access (GET)... ', ending='')
        client.force_authenticate(user=simple_user)
        response = client.get(url)
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('OK (200 OK)'))
        else:
            self.stdout.write(self.style.ERROR(f'FAIL (Got {response.status_code})'))

        # SCENARIO 3: User Access (POST) -> Should be forbidden (can_create=False)
        self.stdout.write('3. User Access (POST)... ', ending='')
        # Note: View doesn't have POST, but Permission check happens FIRST.
        # If permission works, we get 403. If permission is ignored/broken and it hits view, we get 405.
        response = client.post(url, {'title': 'Bad Report'})
        if response.status_code == 403:
            self.stdout.write(self.style.SUCCESS('OK (403 Forbidden) - RBAC blocked write access'))
        else:
            self.stdout.write(self.style.ERROR(f'FAIL (Got {response.status_code})'))

        # SCENARIO 4: Admin Access (POST) -> Should be allowed by RBAC (but 405 by View)
        self.stdout.write('4. Admin Access (POST)... ', ending='')
        client.force_authenticate(user=admin_user)
        response = client.post(url, {'title': 'Good Report'})
        
        # Admin has can_create=True. 
        # So RbacPermission returns True.
        # The View does NOT implement `post` method, so DRF returns 405 Method Not Allowed.
        # If we got 403, it would mean Admin was blocked (Bad).
        # If we got 405, it means Admin passed security and hit the view logic (Good).
        if response.status_code == 405:
            self.stdout.write(self.style.SUCCESS('OK (405 Method Not Allowed) - RBAC granted access, View handled method missing'))
        elif response.status_code == 201:
             self.stdout.write(self.style.SUCCESS('OK (201 Created)'))
        else:
            self.stdout.write(self.style.ERROR(f'FAIL (Got {response.status_code}) - Expected 405 (Access Granted)'))

        self.stdout.write(self.style.WARNING('\n--- TEST COMPLETE ---'))
