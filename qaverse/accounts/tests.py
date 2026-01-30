from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User, EmailOTP
from unittest.mock import patch

class PasswordManagementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='old_password', fullname="Test User")
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        url = '/api/v1/auth/change-password/'
        data = {
            'old_password': 'old_password',
            'new_password': 'new_password123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password123'))

    def test_change_password_invalid(self):
        url = '/api/v1/auth/change-password/'
        data = {
            'old_password': 'wrong_password',
            'new_password': 'new_password123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('django.core.mail.send_mail')
    def test_password_reset_flow(self, mock_send_mail):
        # 1. Request OTP
        url_request = '/api/v1/auth/password-reset/request/'
        self.client.logout()  # Unauthenticated
        response = self.client.post(url_request, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check email sent
        self.assertTrue(mock_send_mail.called)
        
        # Verify OTP created
        otp_obj = EmailOTP.objects.latest('created_at')
        self.assertEqual(otp_obj.email, 'test@example.com')
        self.assertEqual(otp_obj.purpose, 'PASSWORD_RESET')
        self.assertFalse(otp_obj.is_used)

        # Verify call args
        args, kwargs = mock_send_mail.call_args
        self.assertIn('html_message', kwargs)
        # Check if OTP code is in the HTML message
        self.assertIn(otp_obj.otp_code, kwargs['html_message'])
        
        # 2. Verify OTP
        url_verify = '/api/v1/auth/password-reset/verify/'
        response = self.client.post(url_verify, {'email': 'test@example.com', 'otp': otp_obj.otp_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Confirm Reset
        url_confirm = '/api/v1/auth/password-reset/confirm/'
        new_pass = 'reset_password123'
        response = self.client.post(url_confirm, {
            'email': 'test@example.com', 
            'otp': otp_obj.otp_code,
            'new_password': new_pass
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pass))
        
        # Verify OTP used
        otp_obj.refresh_from_db()
        self.assertTrue(otp_obj.is_used)
        
        # Verify cannot use OTP again
        response = self.client.post(url_confirm, {
            'email': 'test@example.com', 
            'otp': otp_obj.otp_code,
            'new_password': 'another_password'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AccountVerificationTests(APITestCase):
    @patch('django.core.mail.send_mail')
    def test_register_verification_flow(self, mock_send_mail):
        # 1. Register
        url = '/api/v1/auth/register/'
        data = {
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'password123',
            'fullname': 'New User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Please verify your email", response.data['message'])
        
        # Verify user is created but inactive
        user = User.objects.get(email='newuser@example.com')
        self.assertFalse(user.is_active)
        
        # Verify OTP created
        otp_obj = EmailOTP.objects.latest('created_at')
        self.assertEqual(otp_obj.email, 'newuser@example.com')
        self.assertEqual(otp_obj.purpose, 'ACCOUNT_ACTIVATION')
        
        # Verify email sent with OTP
        self.assertTrue(mock_send_mail.called)
        args, kwargs = mock_send_mail.call_args
        self.assertIn(otp_obj.otp_code, kwargs['html_message'])
        
        # 2. Verify Account
        url_verify = '/api/v1/auth/verify-account/'
        response = self.client.post(url_verify, {
            'email': 'newuser@example.com',
            'otp': otp_obj.otp_code
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user is now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Verify login works
        url_login = '/api/v1/auth/login/'
        response = self.client.post(url_login, {
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
