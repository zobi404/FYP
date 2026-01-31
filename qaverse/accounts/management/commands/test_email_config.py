from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Test email configuration and attempt to send a test email'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting email configuration test...'))
        
        # 1. Print current settings (masking sensitive data)
        self.stdout.write(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not Set')}")
        self.stdout.write(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not Set')}")
        self.stdout.write(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not Set')}")
        self.stdout.write(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not Set')}")
        
        user = getattr(settings, 'EMAIL_HOST_USER', None)
        password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        
        if user:
            self.stdout.write(f"EMAIL_HOST_USER: {user[:3]}***{user[-3:] if len(user) > 3 else ''} (Set)")
        else:
            self.stdout.write(self.style.ERROR("EMAIL_HOST_USER: Not Set"))

        if password:
            self.stdout.write(f"EMAIL_HOST_PASSWORD: {'*' * 5} (Set)")
        else:
            self.stdout.write(self.style.ERROR("EMAIL_HOST_PASSWORD: Not Set"))

        # 2. Attempt to send email
        if not user:
            self.stdout.write(self.style.ERROR("Cannot attempt to send email without EMAIL_HOST_USER"))
            return

        self.stdout.write("\nAttempting to send test email...")
        try:
            send_mail(
                subject='Test Email from QAVerse Staging',
                message='If you receive this, your email configuration is working correctly.',
                from_email=user,
                recipient_list=[user], # Send to self
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully sent test email to {user}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send email. Error: {str(e)}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
