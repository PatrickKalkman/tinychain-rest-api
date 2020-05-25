from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import DeviceToken

from tinychain.serializers import DeviceTokenSerializer


DEVICETOKENS_URL = reverse('tinychain:devicetoken-list')


class PublicDeviceTokensTests(TestCase):
    """Test the publicly available devicetokens API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving device tokens"""
        res = self.client.get(DEVICETOKENS_URL)

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
        DeviceToken.objects.create(user=self.user,
                                   device_type='IOS',
                                   token='123123123123')
        DeviceToken.objects.create(user=self.user,
                                   device_type='WIN',
                                   token='454454521232')

        res = self.client.get(DEVICETOKENS_URL)

        deviceTokens = DeviceToken.objects.all().order_by(
            '-device_type')
        serializer = DeviceTokenSerializer(deviceTokens, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_devicetokens_limited_to_user(self):
        """Test that alerts returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@simpletechture.nl',
            'password1234'
        )
        DeviceToken.objects.create(user=user2,
                                   device_type='IOS',
                                   token='123123123123')
        deviceToken = DeviceToken.objects.create(user=self.user,
                                                 device_type='WIN',
                                                 token='454454521232')

        res = self.client.get(DEVICETOKENS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['token'],
                         deviceToken.token)

    def test_create_device_token_succeeds(self):
        payload = {
            "device_type": "IOS",
            "token": "12312312321"
        }
        res = self.client.post(DEVICETOKENS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeviceToken.objects.count(), 1)

    def test_delete_device_token_succeeds(self):
        devicetoken = DeviceToken.objects.create(user=self.user,
                                                 device_type='IOS',
                                                 token='123123123123')

        res = self.client.delete(f'{DEVICETOKENS_URL}{devicetoken.id}/')

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DeviceToken.objects.count(), 0)
