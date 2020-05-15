from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Alert

from tinychain.serializers import AlertSerializer


ALERTS_URL = reverse('tinychain:alert-list')


class PublicAlertsTests(TestCase):
    """Test the publicly available alerts API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving alerts"""
        res = self.client.get(ALERTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAlertsApiTests(TestCase):
    """Test the authorized user alerts API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@simpletechture.nl',
            'test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_alers(self):
        """Test retrieving alerts"""
        Alert.objects.create(user=self.user,
                             exchange='kraken',
                             coinpair='EUR:BTC',
                             indicator='>',
                             limit=8200.00)
        Alert.objects.create(user=self.user,
                             exchange='kraken',
                             coinpair='EUR:ETH',
                             indicator='<',
                             limit=150.00)

        res = self.client.get(ALERTS_URL)

        alerts = Alert.objects.all().order_by('-exchange')
        serializer = AlertSerializer(alerts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_alerts_limited_to_user(self):
        """Test that alerts returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@simpletechture.nl',
            'password1234'
        )
        Alert.objects.create(user=user2,
                             exchange='Kraken',
                             coinpair='EUR:BTC',
                             indicator='>',
                             limit=8200.00)
        alert = Alert.objects.create(user=self.user,
                                     exchange='Binance',
                                     coinpair='EUR:ETH',
                                     indicator='<',
                                     limit=150.00)

        res = self.client.get(ALERTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['coinpair'], alert.coinpair)
