from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from gamification.models import XPTransaction

class XPTransactionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='tester@example.com', password='password', role='tester')
        self.client.force_authenticate(user=self.user)

    def test_get_total_xp(self):
        # Initial check (0 XP)
        url = reverse('xptransaction-total')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_xp'], 0)

        # Add some transactions
        XPTransaction.objects.create(user=self.user, amount=50, source='bonus')
        XPTransaction.objects.create(user=self.user, amount=30, source='bug_report_approved')

        # Check updated total
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_xp'], 80)

class LeaderboardTests(APITestCase):
    def test_leaderboard_avatar(self):
        # Create user with avatar
        user = User.objects.create_user(
            email='avatar_user@example.com', 
            password='password', 
            role='tester',
            avatar_url='http://example.com/avatar.png'
        )
        # Give some XP so they appear in leaderboard
        XPTransaction.objects.create(user=user, amount=10, source='test')
        
        url = reverse('leaderboard-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        found = False
        for entry in response.data:
            if entry['email'] == 'avatar_user@example.com':
                self.assertEqual(entry['avatar_url'], 'http://example.com/avatar.png')
                found = True
                break
        self.assertTrue(found, "User not found in leaderboard")
