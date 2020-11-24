from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


REGISTER_USER_API = reverse('account:register')
LOGIN_USER_API = reverse('account:login')
VERIFY_TOKEN_API = reverse('account:token_verify')
REFRESH_TOKEN_API = reverse('account:token_refresh')
USER_INFO_API = reverse('account:me')


USER_PAYLOAD = {
    'email': 'user1@test.com',
    'password': 'password'
}


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class UserTokenGenerationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email='email@email.com',
            password='password'
        )
        self.client.force_login(self.admin_user)
        self.user = create_user(**USER_PAYLOAD)

    def test_tokens_generated_when_login_success(self):
        res = self.client.post(LOGIN_USER_API, USER_PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', res.data)
        self.assertIn('refresh', res.data['tokens'])

    def test_tokens_generated_when_login_fail(self):
        res = self.client.post(LOGIN_USER_API, { 'email': 'user1@test.com', 'password': 'hi' })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('tokens', res.data)
        self.assertNotIn('refresh', res.data)

    def test_tokens_generated_are_verified(self):
        res = self.client.post(LOGIN_USER_API, USER_PAYLOAD)

        accesstoken = res.data.get('tokens').get('access')
        refreshtoken = res.data.get('tokens').get('refresh')
        # Check accesstoken and refreshtoken are given back
        self.assertIsNotNone(accesstoken)
        self.assertIsNotNone(refreshtoken)

        # check accesstoken is verified
        res = self.client.post(VERIFY_TOKEN_API, { 'token': accesstoken })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check refreshtoken is verified
        res = self.client.post(VERIFY_TOKEN_API, { 'token': refreshtoken })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check random string is not verified
        res = self.client.post(VERIFY_TOKEN_API, { 'token': 'random string token' })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refreshed_is_valid(self):
        res = self.client.post(LOGIN_USER_API, USER_PAYLOAD)
        refreshtoken = res.data.get('tokens').get('refresh')
        accesstoken = res.data.get('tokens').get('access')

        # send refresh token to refresh
        res = self.client.post(REFRESH_TOKEN_API, { 'refresh': refreshtoken })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        newaccesstoken = res.data.get('access')

        # make sure two tokens are different
        self.assertNotEqual(accesstoken, newaccesstoken)

        # make sure new token is verified
        res = self.client.post(VERIFY_TOKEN_API, { 'token': newaccesstoken })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_refresh_fails(self):
        res = self.client.post(REFRESH_TOKEN_API, { 'refresh': 'randomtokenthatshouldnotwork' })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_fails_without_token(self):
        res = self.client.post(LOGIN_USER_API, USER_PAYLOAD)
        accesstoken = res.data.get('tokens').get('access')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + accesstoken)
        res = self.client.get(USER_INFO_API)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('email', res.data)
        self.assertNotIn('password', res.data)

        self.client.credentials()
        res = self.client.get(USER_INFO_API)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
