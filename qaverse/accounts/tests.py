from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/auth/register/'
        self.login_url = '/api/v1/auth/login/'
        self.profile_url = '/api/v1/auth/profile/'
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123',
            'fullname': 'Test User',
            'role': 'tester'
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

    def test_login_user(self):
        self.client.post(self.register_url, self.user_data)
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_profile_view(self):
        self.client.post(self.register_url, self.user_data)
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        login_response = self.client.post(self.login_url, login_data)
        token = login_response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_profile(self):
        self.client.post(self.register_url, self.user_data)
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        login_response = self.client.post(self.login_url, login_data)
        token = login_response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        update_data = {'bio': 'I am a tester'}
        response = self.client.patch(self.profile_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'I am a tester')
