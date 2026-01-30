from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from projects.models import Project
from bug_reports.models import BugReport, BugComment
from notifications.models import Notification

class CommunicationTests(APITestCase):
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
        self.bug_report = BugReport.objects.create(
            project=self.project,
            tester=self.tester,
            title='Test Bug',
            description='Description',
            steps_to_reproduce='Steps',
            category='ui',
            severity='low'
        )

    def test_notification_on_bug_creation(self):
        # Already created in setUp, let's check
        notif = Notification.objects.filter(recipient=self.maintainer).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, self.tester)
        self.assertIn('reported a new bug', notif.verb)

    def test_notification_on_status_change(self):
        self.client.force_authenticate(user=self.maintainer)
        url = reverse('bugreport-approve', args=[self.bug_report.id])
        self.client.post(url)
        
        notif = Notification.objects.filter(recipient=self.tester).first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, self.maintainer)
        self.assertIn('updated status', notif.verb)

    def test_threaded_comments_and_notification(self):
        self.client.force_authenticate(user=self.tester)
        # Tester comments
        comment = BugComment.objects.create(
            bug_report=self.bug_report,
            user=self.tester,
            text='Found more info'
        )
        # Notify maintainer
        notif = Notification.objects.filter(recipient=self.maintainer).order_by('-id').first()
        self.assertIn('commented on your bug report', notif.verb)

        # Maintainer replies
        self.client.force_authenticate(user=self.maintainer)
        reply = BugComment.objects.create(
            bug_report=self.bug_report,
            user=self.maintainer,
            text='Thanks, will check',
            parent=comment
        )
        # Notify tester (parent comment owner)
        notif = Notification.objects.filter(recipient=self.tester).order_by('-id').first()
        self.assertIn('commented on your bug report', notif.verb)
        
        # Verify threaded response in API
        url = reverse('bugreport-detail', args=[self.bug_report.id])
        response = self.client.get(url)
        comments = response.data['comments']
        self.assertEqual(len(comments[0]['replies']), 1)
        self.assertEqual(comments[0]['replies'][0]['text'], 'Thanks, will check')

    def test_list_performance(self):
        # Create 20 notifications for the maintainer
        # Using bug report as target
        for i in range(20):
            Notification.objects.create(
                recipient=self.maintainer,
                actor=self.tester,
                verb='did something',
                target=self.bug_report
            )
            
        self.client.force_authenticate(user=self.maintainer)
        url = reverse('notification-list')

        # Should be optimized: 1 user, 1 count, 1 notifications+actor+content_type, 1 target (prefetch generic)
        # Note: Generic prefetch might do one query per content type. Here only BugReport.
        with self.assertNumQueries(lambda n: n < 10):
            response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_structure(self):
        # Verify object_name is present
        self.client.force_authenticate(user=self.maintainer)
        url = reverse('notification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check first notification (newest)
        # Should be related to bug creation if ran in isolation, or the loop above
        # But we know self.bug_report and self.project have titles.
        
        # Checking if at least one notification has object_name populated correctly
        results = response.data
        if 'results' in results: # Pagination
            results = results['results']
            
        self.assertTrue(len(results) > 0)
        first_notif = results[0]
        self.assertIn('object_name', first_notif)
        self.assertTrue(first_notif['object_name']) # Should not be None or empty
