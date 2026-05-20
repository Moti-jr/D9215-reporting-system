from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from d9215.models import UserCredential


class Command(BaseCommand):
    help = 'Create or update a user credential stored in public.user_credentials'

    def add_arguments(self, parser):
        parser.add_argument('user_id', help='UUID of the user (matches public.users.id)')
        parser.add_argument('password', help='Plaintext password to hash')
        parser.add_argument('--force', action='store_true', help='Overwrite existing credential')

    def handle(self, *args, **options):
        user_id = options['user_id']
        password = options['password']
        force = options['force']

        password_hash = make_password(password)

        obj, created = UserCredential.objects.get_or_create(user_id=user_id, defaults={'password_hash': password_hash})
        if not created:
            if force:
                obj.password_hash = password_hash
                obj.save(update_fields=['password_hash'])
                self.stdout.write(self.style.SUCCESS(f'Updated credential for {user_id}'))
            else:
                self.stdout.write(self.style.WARNING(f'Credential for {user_id} already exists; use --force to overwrite'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created credential for {user_id}'))
