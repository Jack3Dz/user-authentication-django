from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status


class UsersTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')

        # URL for creating an user.
        self.create_url = reverse('user-create')

        user = User.objects.get(username='testuser')
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_create_user(self):
        """
        Ensure we can create a new user and a valid token is created with it.
        """

        data = {
            'username': 'foobar',
            'email': 'foobar@example.com',
            'password': 'foobarpassword',
        }

        response = self.client.post(self.create_url, data, format='json')
        user = User.objects.latest('id')
        token = Token.objects.get(user=user)
        self.assertEquals(User.objects.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['token'], token.key)
        self.assertFalse('password' in response.data)

    def test_create_user_with_short_password(self):
        """
        Ensure user is not created for password lengths less than 8.
        """
        data = {
            'username': 'foobar',
            'email': 'foobarbaz@example.com',
            'password': 'foo'
        }

        self.response_field(data, 'password')

    def test_create_user_with_no_password(self):
        data = {
            'username': 'foobar',
            'email': 'foobarbaz@example.com',
            'password': 'foo'
        }

        self.response_field(data, 'password')

    def test_create_user_with_too_long_username(self):
        data = {
            'username': 'foo' * 30,
            'email': 'foobarbaz@example.com',
            'password': 'foobar'
        }

        self.response_field(data, 'username')

    def test_create_user_with_no_username(self):
        data = {
            'username': '',
            'email': 'foobarbaz@example.com',
            'password': 'foobar'
        }

        self.response_field(data, 'username')

    def test_create_user_with_preexisting_username(self):
        data = {
            'username': 'testuser',
            'email': 'user@example.com',
            'password': 'testuser'
        }

        self.response_field(data, 'username')

    def test_create_user_with_preexisting_email(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testuser'
        }

        self.response_field(data, 'email')

    def test_create_user_with_invalid_email(self):
        data = {
            'username': 'testuser',
            'email': 'testing',
            'password': 'testuser'
        }

        self.response_field(data, 'email')

    def test_create_user_with_no_email(self):
        data = {
            'username': 'testuser',
            'email': '',
            'password': 'testuser'
        }

        self.response_field(data, 'email')

    def response_field(self, data, field):
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data[field]), 1)
