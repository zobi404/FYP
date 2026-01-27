import uuid
from django.db import models
from accounts.models import User

class XPTransaction(models.Model):
    SOURCE_CHOICES = (
        ('bug_report_approved', 'Bug Report Approved'),
        ('bonus', 'Bonus'),
        ('admin_adjustment', 'Admin Adjustment'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='xp_transactions')
    amount = models.PositiveIntegerField()
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    reference_id = models.CharField(max_length=100, null=True, blank=True, help_text="ID of the related object (e.g. BugReport)")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.amount} XP from {self.source}"

class Badge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon_url = models.URLField(null=True, blank=True, help_text="URL to badge icon")
    xp_required = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.email} earned {self.badge.name}"
