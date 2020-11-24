from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import AccessLog


REGISTER_USER_API = reverse('account:register')
LOGIN_USER_API = reverse('account:login')
VERIFY_TOKEN_API = reverse('account:token_verify')


class AccessLogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='user1@email.com',
            password='password',
        )

    def test_register_user_logged(self):
        self.client.post(REGISTER_USER_API, { 'email': 'user1@nav.com', 'password': 'testuser1' })
        self.assertEqual(1, AccessLog.objects.all().count())

        # after failure
        self.client.post(REGISTER_USER_API, { 'email': 'user1@nav.com', 'password': 'testuser1' })
        self.assertEqual(2, AccessLog.objects.all().count())

    def test_login_user_logged(self):
        self.client.post(REGISTER_USER_API, { 'email': 'user1@nav.com', 'password': 'testuser1' })
        self.assertEqual(1, AccessLog.objects.all().count())

        self.client.post(LOGIN_USER_API, { 'email': 'user1@nav.com', 'password': 'testuser1' })
        self.assertEqual(2, AccessLog.objects.all().count())

        self.client.post(LOGIN_USER_API, { 'email': 'a@nav.com', 'password': 'testuser1' })
        self.assertEqual(3, AccessLog.objects.all().count())


    def test_verify_token_logged(self):
        res = self.client.post(VERIFY_TOKEN_API, { 'token': 'token' })
        self.assertEqual(1, AccessLog.objects.all().count())
