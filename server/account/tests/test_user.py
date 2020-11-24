from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


REGISTER_USER_API = reverse('account:register')
LOGIN_USER_API = reverse('account:login')
USER_INFO_API = reverse('account:me')
EMAIL_CHECK_API = reverse('account:email-check')

USER_PAYLOAD = {
    'email': 'user1@test.com',
    'password': 'password'
}


class UserTests(TestCase):
    def test_create_user_with_email_successful(self):
        email = "tester@berkeley.edu"
        password = "testing1212"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_without_password_successful(self):
        email = "tester@berkeley.edu"
        password = ""
        user = get_user_model().objects.create_user(
            email=email,
            password=''
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = "tetster@BERKELEY.COM"
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            'testeremail@nv.com,',
            'swag12345'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class RegisterUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_valid_user_success(self):
        res = self.client.post(REGISTER_USER_API, {'email': 'user1@nav.com', 'password': 'testuser1'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', res.data)
        self.assertIn('email', res.data)

    def test_register_user_invalid_password_fail(self):
        res = self.client.post(REGISTER_USER_API, {'email': 'user1@nav.com', 'password': '12345'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_invalid_email_fail(self):
        res = self.client.post(REGISTER_USER_API, {'email': 'user1nav.com', 'password': '1234567'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_fail(self):
        res = self.client.post(REGISTER_USER_API, {'email': 'user1@nav.com', 'password': 'testuser1'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(REGISTER_USER_API, {'email': 'user1@nav.com', 'password': 'testuser1'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class LoginUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(**USER_PAYLOAD)


    def test_login_user_success(self):
        res = self.client.post(LOGIN_USER_API, USER_PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', res.data)
        self.assertIn('refresh', res.data['tokens'])
        self.assertIn('access', res.data['tokens'])

    def test_login_user_fail(self):
        res = self.client.post(LOGIN_USER_API, {'email': 'randomemail@naver.com', 'password': 'notcorrect'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(LOGIN_USER_API, {'email': USER_PAYLOAD['email'], 'password': 'notcorrect'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class UserDetailsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(**USER_PAYLOAD)

    def test_get_user_details_success(self):
        res = self.client.post(LOGIN_USER_API, USER_PAYLOAD)
        access_token = res.data.get('tokens').get('access')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        res = self.client.get(USER_INFO_API)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('email', res.data)
        self.assertNotIn('password', res.data)

    def test_get_user_details_fail(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'accesstoken')
        res = self.client.get(USER_INFO_API)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UpdateUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(**USER_PAYLOAD)

    def test_update_valid_user_success(self):
        res = self.client.post(LOGIN_USER_API, USER_PAYLOAD)
        tokens = res.data.get('tokens')
        access_token = tokens.get('access')

        # try to update user email
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        res = self.client.put(USER_INFO_API, {'email': 'user2@nav.com'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('updated'))

        #check cannot login with previous data
        res = self.client.post(LOGIN_USER_API, {'email': 'user1@nav.com', 'password': 'testuser1'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        #check can login with new data
        res = self.client.post(LOGIN_USER_API, {'email': 'user2@nav.com', 'password': 'password'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        access_token = res.data.get('tokens').get('access')

        #change password
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        res = self.client.put(USER_INFO_API, {'password': 'testuser2'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        #check cannot login with previous data
        res = self.client.post(LOGIN_USER_API, {'email': 'user2@nav.com', 'password': 'password'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        #check can login with new data
        res = self.client.post(LOGIN_USER_API, {'email': 'user2@nav.com', 'password': 'testuser2'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_invalid_data_fail(self):
        res = self.client.post(LOGIN_USER_API, USER_PAYLOAD)
        tokens = res.data.get('tokens')
        access_token = tokens.get('access')

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        res = self.client.put(USER_INFO_API, {'email': 'wronglyformattedemail'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data.get('updated'), False)

class EmailCheckTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_email_check_success(self):
        res = self.client.get(EMAIL_CHECK_API, {'email': 'user1@nav.com'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('available'))

    def test_invalid_email_check_fail(self):
        res = self.client.get(EMAIL_CHECK_API, {'email': 'user1@navcom'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.get(EMAIL_CHECK_API, {'email': '123.1'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_check_fail(self):
        res = self.client.get(EMAIL_CHECK_API, {'email': 'user1@nav.com'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get('available'))

        self.client.post(REGISTER_USER_API, {'email': 'user1@nav.com', 'password': 'testuser1'})
        res = self.client.get(EMAIL_CHECK_API, {'email': 'user1@nav.com'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
