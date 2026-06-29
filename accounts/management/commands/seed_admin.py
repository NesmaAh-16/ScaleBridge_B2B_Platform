from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Seed the database with a default admin user'

    def handle(self, *args, **kwargs):
        email    = 'admin@scalebridge.com'
        password = 'Admin@1234'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Admin already exists: {email}'))
            return

        User.objects.create_superuser(
            username=email,
            email=email,
            password=password,
            first_name='Scale',
            last_name='Bridge',
            role='Admin',
        )

        self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        self.stdout.write(f'  Email   : {email}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(self.style.WARNING('Change the password after first login!'))
