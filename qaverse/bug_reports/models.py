from django.db import models
from accounts.models import User
from projects.models import Project

class BugReport(models.Model):
    CATEGORY_CHOICES = (
        ('ui', 'UI'),
        ('functionality', 'Functionality'),
        ('performance', 'Performance'),
        ('security', 'Security'),
    )
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('resolved', 'Resolved'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bug_reports')
    tester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_bugs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    steps_to_reproduce = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

class BugAttachment(models.Model):
    bug_report = models.ForeignKey(BugReport, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='bug_reports/attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.bug_report.title}"

class BugComment(models.Model):
    bug_report = models.ForeignKey(BugReport, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.bug_report.title}"
