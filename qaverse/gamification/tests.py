from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from projects.models import Project
from bug_reports.models import BugReport
from gamification.models import XPTransaction

class GamificationTests(APITestCase):
    def setUp(self):
        self.tester = User.objects.create_user(email='tester@example.com', password='password', role='tester')
        self.maintainer = User.objects.create_user(email='maintainer@example.com', password='password', role='maintainer')
        self.project = Project.objects.create(
            maintainer=self.maintainer,
            title='Test Project',
            description='Test Description',
            technology_stack='Django',
            testing_url='http://example.com',
            category='web',
            status='active'
        )

    def test_xp_awarded_on_approval(self):
        bug_report = BugReport.objects.create(
            project=self.project,
            tester=self.tester,
            title='Critical Bug',
            description='Description',
            steps_to_reproduce='Steps',
            category='functionality',
            severity='critical'
        )
        
        self.client.force_authenticate(user=self.maintainer)
        url = reverse('bugreport-approve', args=[bug_report.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify XPTransaction creation
        transaction = XPTransaction.objects.get(user=self.tester)
        self.assertEqual(transaction.amount, 100) # Critical bug = 100 XP
        self.assertEqual(transaction.source, 'bug_report_approved')

    def test_leaderboard(self):
        # Create another tester with different XP
        tester2 = User.objects.create_user(email='tester2@example.com', password='password', role='tester')
        
        XPTransaction.objects.create(user=self.tester, amount=100, source='bonus')
        XPTransaction.objects.create(user=tester2, amount=200, source='bonus')
        
        url = reverse('leaderboard-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Tester 2 should be first
        self.assertEqual(response.data[0]['email'], tester2.email)
        self.assertEqual(response.data[0]['total_xp'], 200)
        # Tester 1 should be second
        self.assertEqual(response.data[1]['email'], self.tester.email)
        self.assertEqual(response.data[1]['total_xp'], 100)
