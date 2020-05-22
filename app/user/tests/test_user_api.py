from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
CREATE_APPLE_USER_URL = reverse('user:createapple')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
APPLE_ME_URL = reverse('user:appleme')
ME_VALIDATE = reverse('user:validate')


def create_user(**params):
    """Helper function to create new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating using with a valid payload is successful"""
        payload = {
            'email': 'test@simpletechture.nl',
            'password': 'testpass',
            'name': 'name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(
            user.check_password(payload['password'])
        )
        self.assertFalse(user.is_verified)
        self.assertNotIn('password', res.data)
        self.assertIsNotNone(user.verification_id)

    def test_create_valid_apple_user_success(self):
        """Test creating apple user with a valid payload is successful"""
        payload = {
            'email': '',
            'password': '',
            'name': '',
            'apple_user_id': '123123.232334aa'
        }
        res = self.client.post(CREATE_APPLE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(
            user.check_password(payload['password'])
        )
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_apple_user)

        self.assertNotIn('password', res.data)
        self.assertEqual(payload['apple_user_id'], user.apple_user_id)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {'email': 'test@simpletechture.nl',
                   'password': 'testpass',
                   'name': 'Test'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {'email': 'test@simpletechture.nl',
                   'password': 'pw',
                   'name': 'Test'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'test@simpletechture.nl', 'password': 'testpass'}
        user = create_user(**payload)
        user.is_verified = True
        user.save()
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_no_token_is_created_when_not_verified(self):
        """Test that no token can be created for the user when not verified."""
        payload = {'email': 'test@simpletechture.nl', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_token_is_created_when_not_active(self):
        """Test that no token can be created for the user when not active."""
        payload = {'email': 'test@simpletechture.nl', 'password': 'testpass',
                   'is_verified': 'True'}
        user = create_user(**payload)
        user.is_active = False
        user.save()
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@simpletechture.nl', password='testpass')
        payload = {'email': 'test@simpletechture.nl', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doens't exist"""
        payload = {'email': 'test@simpletechture.nl', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verification_verifies_user(self):
        """Test that calling the verification link verifies the user"""
        self.user = create_user(
            email='test@londonappdev.com',
            password='testpass',
            name='name',
        )
        url = f'{ME_VALIDATE}?verification_id={self.user.verification_id}'
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)

    def test_no_verification_id_returns_bad_request(self):
        """Test that calling without verification id return error"""
        res = self.client.get(ME_VALIDATE)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_existing_verification_id_returns_bad_request(self):
        """Test that calling not existing verification id return error"""
        uuid = '2cae0c47-2e62-4cc4-9d7e-6edc96e9d042'
        url = f'{ME_VALIDATE}?verification_id={uuid}'
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@simpletechture.nl',
            password='testpass',
            name='fname',
        )
        self.appleuser = create_user(
            email='testapple@simpletechture.nl',
            password='testpass',
            name='apple name',
            apple_user_id='1234567890',
            is_apple_user=True,
            is_verified=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_retrieve_appleuser_profile_success(self):
        """Test retrieving profile for apple user"""

        url = f'{APPLE_ME_URL}?apple_user_id={self.appleuser.apple_user_id}'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.appleuser.name,
            'email': self.appleuser.email,
        })

    def test_retrieve_appleuser_notfound(self):
        """Test retrieving profile for non existing apple user"""

        url = f'{APPLE_ME_URL}?apple_user_id=1234'
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_user_profile(self):
        """Test deleting the user profile for authenticated user"""
        res = self.client.delete(ME_URL)
        self.user.refresh_from_db()

        self.assertFalse(self.user.is_active)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
