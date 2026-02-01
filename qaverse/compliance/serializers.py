from rest_framework import serializers
from .models import ComplianceAudit

class ComplianceAuditRequestSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)

class ComplianceAuditResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceAudit
        fields = ['id', 'url', 'readiness_score', 'report_markdown', 'report_pdf', 'tech_stack_raw', 'headers_raw', 'created_at']
        read_only_fields = fields
