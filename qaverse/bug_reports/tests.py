from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from projects.models import Project
from bug_reports.models import BugReport

class BugReportTests(APITestCase):
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

    def test_create_bug_report(self):
        url = reverse('bugreport-list')
        data = {
            'project': self.project.id,
            'title': 'Test Bug',
            'description': 'Test Bug Description',
            'steps_to_reproduce': '1. Do something',
            'category': 'ui',
            'severity': 'low'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BugReport.objects.count(), 1)
        self.assertEqual(BugReport.objects.get().status, 'pending')

    def test_approve_bug_report(self):
        bug_report = BugReport.objects.create(
            project=self.project,
            tester=self.tester,
            title='Test Bug',
            description='Test Description',
            steps_to_reproduce='Steps',
            category='ui',
            severity='low'
        )
        url = reverse('bugreport-approve', args=[bug_report.id])
        
        # Test as tester (should fail)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test as maintainer
        self.client.force_authenticate(user=self.maintainer)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bug_report.refresh_from_db()
        self.assertEqual(bug_report.status, 'approved')

    def test_reject_bug_report(self):
        bug_report = BugReport.objects.create(
            project=self.project,
            tester=self.tester,
            title='Test Bug',
            description='Test Description',
            steps_to_reproduce='Steps',
            category='ui',
            severity='low'
        )
        url = reverse('bugreport-reject', args=[bug_report.id])
        
        self.client.force_authenticate(user=self.maintainer)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bug_report.refresh_from_db()
        self.assertEqual(bug_report.status, 'rejected')

    def test_resolve_bug_report(self):
        bug_report = BugReport.objects.create(
            project=self.project,
            tester=self.tester,
            title='Test Bug',
            description='Test Description',
            steps_to_reproduce='Steps',
            category='ui',
            severity='low',
            status='approved'
        )
        url = reverse('bugreport-resolve', args=[bug_report.id])
        
        self.client.force_authenticate(user=self.maintainer)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bug_report.refresh_from_db()
        self.assertEqual(bug_report.status, 'resolved')

    def test_list_performance(self):
        # Create 10 bugs with attachments and comments to test prefetch
        for i in range(10):
            b = BugReport.objects.create(
                project=self.project,
                tester=self.tester,
                title=f'Bug {i}',
                description='Desc',
                steps_to_reproduce='Steps',
                category='ui',
                severity='low'
            )
            # Add nested data
            from bug_reports.models import BugAttachment, BugComment
            BugAttachment.objects.create(bug_report=b, file_url='http://x.com')
            BugComment.objects.create(bug_report=b, user=self.maintainer, text='Fixing')

        self.client.force_authenticate(user=self.maintainer)
        url = reverse('bugreport-list')
        
        # Checking for O(1) queries instead of O(N)
        # 1 user, 1 count, 1 bugs+project+tester, 1 attachments, 1 comments, 1 comment_users
        with self.assertNumQueries(lambda n: n < 15): 
            response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_recursion_limit(self):
        """Test that circular comment references don't cause recursion error"""
        bug_report = BugReport.objects.create(
            project=self.project,
            tester=self.tester,
            title='Recursion Bug',
            description='Desc',
            steps_to_reproduce='Steps',
            category='ui',
            severity='low'
        )
        
        from bug_reports.models import BugComment
        
        # Create circular reference A -> B -> A
        comment_a = BugComment.objects.create(
            bug_report=bug_report, 
            user=self.maintainer, 
            text='Comment A'
        )
        comment_b = BugComment.objects.create(
            bug_report=bug_report, 
            user=self.maintainer, 
            text='Comment B',
            parent=comment_a
        )
        # Make A a child of B (cycle)
        comment_a.parent = comment_b
        comment_a.save()
            
        url = reverse('bugreport-list')
        self.client.force_authenticate(user=self.maintainer)
        try:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Ensure we got a response and not a crash
            print("Recursion test passed successfully")
        except RecursionError:
            self.fail("RecursionError raised during serialization of circular comments")

