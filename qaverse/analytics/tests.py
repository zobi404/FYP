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

    def test_maintainer_stats(self):
        # Setup specific to this test
        self.client.force_authenticate(user=self.maintainer)
        
        # 1. Active Projects Count
        # self.project is active (created in setUp). Create a paused one.
        Project.objects.create(
            maintainer=self.maintainer, title='Paused Project', category='web', status='paused', 
            description='desc', technology_stack='stack'
        )
        
        # 2. Testers & Bugs
        # Tester (from setUp) creates a bug on active project
        BugReport.objects.create(
            project=self.project, tester=self.tester, title='Bug 1', status='approved', severity='low',
            description='desc', steps_to_reproduce='steps', category='ui'
        )
        
        # Create another tester and bug
        tester2 = User.objects.create_user(email='tester2@example.com', password='password', role='tester')
        BugReport.objects.create(
            project=self.project, tester=tester2, title='Bug 2', status='pending', severity='high',
            description='desc', steps_to_reproduce='steps', category='ui'
        )
        
        # Create a bug by Tester 1 on the Paused project (should still count towards total bugs/testers)
        # Requirement: "testers testing on maintainer projects". Usually implies any project.
        # Requirement: "Total no of bug reports for this maintainer". Usually implies all projects.
        paused_project = Project.objects.get(title='Paused Project')
        BugReport.objects.create(
             project=paused_project, tester=self.tester, title='Bug 3', status='rejected', severity='low',
             description='desc', steps_to_reproduce='steps', category='ui'
        )

        url = reverse('maintainer-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_active_projects'], 1) # Only self.project is active
        self.assertEqual(response.data['total_testers'], 2) # tester and tester2
        self.assertEqual(response.data['total_bugs'], 3) # Bug 1, 2, 3
        self.assertEqual(response.data['approved_bugs'], 1) # Only Bug 1 is approved
