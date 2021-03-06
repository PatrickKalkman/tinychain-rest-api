from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='admin@example.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


def sample_alert(user):
    return models.Alert.objects.create(
        user=user,
        exchange='kraken',
        coinpair='BTC:EUR',
        indicator='>',
        limit=8412.54,
        trigger_value=8515.00
    )


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@simpletechture.nl'
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@SIMPLETECHTURE.nl'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@simpletechture.nl',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_alert_str(self):
        alert = models.Alert.objects.create(
            user=sample_user(),
            exchange='kraken',
            coinpair='BTC:EUR',
            indicator='>',
            limit=8412.54,
            trigger_value=8515.00
        )

        str_alert = (f'({alert.coinpair} {alert.indicator} '
                     f'{alert.limit:.2f}) -> Price = '
                     f'{alert.trigger_value:.2f}')

        self.assertEquals(str(alert), str_alert)

    def test_devicetoken_str(self):
        device_token = models.DeviceToken.objects.create(
            user=sample_user(),
            token='1232312323',
            device_type='IOS'
        )

        self.assertEquals(str(device_token),
                          f'{device_token.device_type} {device_token.token}')

    def test_notificationhistory_str(self):
        user = sample_user()
        notification_history = models.NotificationHistory.objects.create(
            user=user,
            alert=sample_alert(user),
            succeeded=True,
            notification_result='hallo'
        )

        self.assertEquals(str(notification_history),
                          (f'{notification_history.notified_at} '
                           f'{notification_history.succeeded} '
                           f'{notification_history.alert}'))
