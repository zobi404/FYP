from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from projects.models import Project
from bug_reports.models import BugReport
from gamification.models import XPTransaction

class AnalyticsTests(APITestCase):
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
        self.client.force_authenticate(user=self.tester)

    def test_tester_stats(self):
        # Create a bug report and approve it to get XP
        bug = BugReport.objects.create(
            project=self.project, tester=self.tester, title='Bug 1', 
            severity='critical', status='approved'
        )
        XPTransaction.objects.create(user=self.tester, amount=100, source='bug_report_approved', reference_id=bug.id)
        
        # Create another pending bug
        BugReport.objects.create(
            project=self.project, tester=self.tester, title='Bug 2', 
            severity='low', status='pending'
        )

        url = reverse('tester-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_xp'], 100)
        self.assertEqual(response.data['bug_reports_count'], 2)
        self.assertEqual(response.data['approved_bugs_count'], 1)
        self.assertEqual(response.data['success_rate'], 50.0)

    def test_project_stats(self):
        BugReport.objects.create(project=self.project, tester=self.tester, title='B1', severity='critical', status='approved')
        BugReport.objects.create(project=self.project, tester=self.tester, title='B2', severity='low', status='pending')

        url = reverse('project-stats', args=[self.project.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_bugs'], 2)
        self.assertEqual(response.data['status_distribution']['approved'], 1)
        self.assertEqual(response.data['severity_distribution']['critical'], 1)
