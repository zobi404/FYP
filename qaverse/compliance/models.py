from django.db import models
from django.conf import settings

class ComplianceAudit(models.Model):
    maintainer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='compliance_audits'
    )
    url = models.URLField(max_length=500)
    readiness_score = models.IntegerField(default=0)
    report_markdown = models.TextField()
    report_pdf = models.FileField(upload_to='compliance_reports/', blank=True, null=True)
    tech_stack_raw = models.JSONField(default=dict, blank=True)
    headers_raw = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audit for {self.url} by {self.maintainer.email}"
