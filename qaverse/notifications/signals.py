from django.db.models.signals import post_save
from django.dispatch import receiver
from bug_reports.models import BugReport, BugComment
from .models import Notification

@receiver(post_save, sender=BugReport)
def bug_report_notification(sender, instance, created, **kwargs):
    if created:
        # Notify project maintainer about new bug report
        Notification.objects.create(
            recipient=instance.project.maintainer,
            actor=instance.tester,
            verb='reported a new bug in',
            target=instance.project
        )
    else:
        # Notify tester when bug status changes
        Notification.objects.create(
            recipient=instance.tester,
            actor=instance.project.maintainer,
            verb=f'updated status of your bug report to {instance.status}',
            target=instance
        )

@receiver(post_save, sender=BugComment)
def comment_notification(sender, instance, created, **kwargs):
    if created:
        # Determine who to notify
        # If it's a reply, notify the parent comment owner
        if instance.parent:
            recipient = instance.parent.user
        else:
            # If it's a main comment, notify either maintainer or tester
            if instance.user == instance.bug_report.tester:
                recipient = instance.bug_report.project.maintainer
            else:
                recipient = instance.bug_report.tester
        
        if recipient != instance.user:
            Notification.objects.create(
                recipient=recipient,
                actor=instance.user,
                verb='commented on your bug report',
                target=instance.bug_report
            )
