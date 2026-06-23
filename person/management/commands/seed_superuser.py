from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

admin_email = "admin@admin.com"
admin_password = "Admin123!"

class Command(BaseCommand):
    help = "Seed the database with a superuser"

    def handle(self, *args, **kwargs):
        if User.objects.filter(email=admin_email).exists():
            self.stdout.write(f"Superuser with email {admin_email} already exists")
            return

        self.stdout.write(f"Creating superuser with email {admin_email} and password {admin_password}")
        superuser = User.objects.create_superuser(
            username=admin_email,
            email=admin_email,
            password=admin_password
        )
        self.stdout.write(f"Superuser created successfully")