import unittest
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User, Organization, Membership
from rest_framework.test import APIClient
import datetime
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework_simplejwt.tokens import RefreshToken


# End-to-End Test Cases
class RegistrationEndToEndTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user_without_organization(self):
        url = reverse('register')
        data = {
            'email': 'test1@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'phone': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], 'test1@example.com')
        self.assertEqual(response.data['data']['user']['first_name'], 'John')
        self.assertEqual(response.data['data']['user']['last_name'], 'Doe')

    def test_register_user_with_missing_fields(self):
        url = reverse('register')
        missing_fields = ['first_name', 'last_name', 'email', 'password']
        for field in missing_fields:
            data = {
                'email': 'test2@example.com' if field != 'email' else '',
                'first_name': 'John' if field != 'first_name' else '',
                'last_name': 'Doe' if field != 'last_name' else '',
                'password': 'password123' if field != 'password' else '',
                'phone': '1234567890'
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_register_user_with_duplicate_email(self):
        User.objects.create_user(email='test3@example.com', first_name='John', last_name='Doe', password='password123',
                                 phone='1234567890')
        url = reverse('register')
        data = {
            'email': 'test3@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'password456',
            'phone': '0987654321'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_login_user(self):
        User.objects.create_user(email='test4@example.com', first_name='John', last_name='Doe', password='password123',
                                 phone='1234567890')
        url = reverse('login')
        data = {
            'email': 'test4@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], 'test4@example.com')
        self.assertEqual(response.data['data']['user']['firstName'], 'John')
        self.assertEqual(response.data['data']['user']['lastName'], 'Doe')

    def test_login_user_with_invalid_credentials(self):
        User.objects.create_user(email='test5@example.com', first_name='John', last_name='Doe', password='password123',
                                 phone='1234567890')
        url = reverse('login')
        data = {
            'email': 'test5@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# Unit Test Cases
class TokenGenerationUnitTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test6@example.com', first_name='John', last_name='Doe', password='password123')

    def test_token_expiry(self):
        token = RefreshToken.for_user(self.user)
        self.assertTrue(token.access_token)
        token_expiry = make_aware(datetime.datetime.fromtimestamp(token.access_token.payload['exp']))
        self.assertLessEqual(token_expiry, timezone.now() + datetime.timedelta(minutes=60))

    def test_token_contains_correct_user_details(self):
        token = RefreshToken.for_user(self.user)
        user_id_in_token = token.access_token.payload['user_id']
        self.assertEqual(str(self.user.user_id), user_id_in_token)


class OrganizationPermissionUnitTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test7@example.com', first_name='John', last_name='Doe', password='password123')
        self.other_user = User.objects.create_user(email='other@example.com', first_name='Jane', last_name='Smith', password='password456')
        self.organization = Organization.objects.create(name="John's Organization")

    def test_user_cannot_access_unrelated_organization(self):
        self.assertFalse(self.user.organization_set.filter(pk=self.organization.pk).exists())

    def test_user_can_access_own_organization(self):
        Membership.objects.create(user=self.user, organization=self.organization)
        self.assertTrue(self.user.organization_set.filter(pk=self.organization.pk).exists())


if __name__ == '__main__':
    unittest.main()
