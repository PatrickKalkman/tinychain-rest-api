import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin

from core.tasks import send_verification_email


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

    def create_apple_user(self, email, password, **extra_fields):
        """Creates and saves an apple user, """
        """user signed in to the app using their Apple id"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.is_apple_user = True
        user.is_verified = True
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_apple_user = models.BooleanField(default=False)
    apple_user_id = models.CharField(max_length=255, default='')
    is_verified = models.BooleanField(default=False)
    verification_id = models.UUIDField(default=uuid.uuid4, editable=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


def user_post_save(sender, instance, signal, *args, **kwargs):
    if not (instance.is_verified or instance.is_apple_user):
        send_verification_email.delay(instance.pk)


models.signals.post_save.connect(user_post_save, sender=User)


class Alert(models.Model):
    """Alert model to define a custom alert"""
    exchange = models.CharField(max_length=255)
    coinpair = models.CharField(max_length=255)
    indicator = models.CharField(max_length=1)
    limit = models.DecimalField(max_digits=10, decimal_places=5)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.coinpair} {self.indicator} {self.limit}'
