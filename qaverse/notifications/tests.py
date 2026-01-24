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
