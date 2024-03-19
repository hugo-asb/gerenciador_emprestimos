from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.contrib.auth import models as auth_models
from django.dispatch import receiver


class UserManager(auth_models.BaseUserManager):
    def create_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password: str = None,
        is_staff=False,
        is_superuser=False,
    ) -> "User":
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have an username")

        user = self.model(email=self.normalize_email(email))
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.set_password(password)
        user.is_active = True
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str = None,
    ) -> "User":
        user = self.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
        )

        user.save(using=self._db)
        return user


class User(auth_models.AbstractUser):
    first_name = models.CharField(verbose_name="First name", max_length=255)
    last_name = models.CharField(verbose_name="Last name", max_length=255)
    username = models.CharField(
        verbose_name="Username", max_length=255, unique=True, default="default"
    )
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    password = models.CharField(verbose_name="Password", max_length=255)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
