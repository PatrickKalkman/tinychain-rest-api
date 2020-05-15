from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='admin@example.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


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
            limit=8412.54
        )

        self.assertEquals(str(alert),
                          f'{alert.coinpair} {alert.indicator} {alert.limit}')
