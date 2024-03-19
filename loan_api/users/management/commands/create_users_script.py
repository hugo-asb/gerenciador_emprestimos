from django.core.management.base import BaseCommand, CommandError
from users.models import User


class Command(BaseCommand):
    help = "Create some user accounts"

    def handle(self, *args, **options):
        try:
            User.objects.create_superuser(
                username="generated_admin",
                first_name="Admin",
                last_name="Admin",
                email="generated_admin@admin.com",
                password="admin-password",
            )
        except Exception as error:
            raise CommandError(error)

        try:
            User.objects.create_user(
                username="generated_user",
                first_name="User",
                last_name="User",
                email="generated_user@user.com",
                password="user-password",
            )
        except Exception as error:
            raise CommandError(error)
