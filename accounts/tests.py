import datetime
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organization, Membership


class TokenGenerationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', first_name='John', last_name='Doe', password='password123')

    def test_token_expiry(self):
        token = RefreshToken.for_user(self.user)
        self.assertTrue(token.access_token)
        token_expiry = make_aware(datetime.datetime.fromtimestamp(token.access_token.payload['exp']))
        self.assertLessEqual(token_expiry, timezone.now() + datetime.timedelta(minutes=60))


class OrganizationPermissionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', first_name='John', last_name='Doe', password='password123')
        self.other_user = User.objects.create_user(email='other@example.com', first_name='Jane', last_name='Smith', password='password456')
        self.organization = Organization.objects.create(name="John's Organization")

    def test_user_cannot_access_unrelated_organization(self):
        self.assertFalse(self.user.organization_set.filter(pk=self.organization.pk).exists())

    def test_user_can_access_own_organization(self):
        Membership.objects.create(user=self.user, organization=self.organization)
        self.assertTrue(self.user.organization_set.filter(pk=self.organization.pk).exists())


