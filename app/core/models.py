import uuid
from django.utils.translation import gettext_lazy as _
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


def connect():
    models.signals.post_save.connect(user_post_save, sender=User)


"""Only connect email when running in production"""
if not settings.DEBUG:
    connect()


class Alert(models.Model):
    """Alert model to define a custom alert"""
    exchange = models.CharField(max_length=255)
    coinpair = models.CharField(max_length=255)
    indicator = models.CharField(max_length=255)
    limit = models.DecimalField(max_digits=10, decimal_places=5)
    is_active = models.BooleanField(default=False)
    trigger_value = models.DecimalField(max_digits=10,
                                        decimal_places=5,
                                        default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return (f'({self.coinpair} {self.indicator} '
                f'{self.limit:.2f}) -> Price = '
                f'{self.trigger_value:.2f}')


class NotificationHistory(models.Model):
    """Logs all notification and result"""
    notification_result = models.CharField(max_length=255)
    succeeded = models.BooleanField(default=False)
    notified_at = models.DateTimeField(auto_now_add=True, blank=True)
    alert = models.ForeignKey(
        Alert,
        on_delete=models.SET_NULL,
        blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.notified_at} {self.succeeded} {self.alert}'


class DeviceToken(models.Model):
    """Device token model to store device tokens"""

    class DeviceTypes(models.TextChoices):
        IOS = 'IOS', _('IOS')
        ANDROID = 'ADR', _('ANDROID')
        WINDOWS = 'WIN', _('WINDOWS')
        MACOS = 'MAC', _('MACOS')

    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(
        max_length=3,
        choices=DeviceTypes.choices,
        default=DeviceTypes.IOS
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.device_type} {self.token}'
