from rest_framework import serializers
from .models import BugReport, BugAttachment, BugComment
from projects.serializers import ProjectSerializer
from accounts.serializers import UserSerializer

class BugAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BugAttachment
        fields = ['id', 'bug_report', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class BugCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = BugComment
        fields = ['id', 'bug_report', 'user', 'parent', 'text', 'created_at', 'replies']
        read_only_fields = ['user', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return BugCommentSerializer(obj.replies.all(), many=True).data
        return []

class BugReportSerializer(serializers.ModelSerializer):
    tester = serializers.StringRelatedField(read_only=True)
    attachments = BugAttachmentSerializer(many=True, read_only=True)
    comments = BugCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = BugReport
        fields = [
            'id', 'project', 'tester', 'title', 'description', 
            'steps_to_reproduce', 'category', 'severity', 
            'status', 'created_at', 'updated_at', 
            'attachments', 'comments'
        ]
        read_only_fields = ['tester', 'status', 'created_at', 'updated_at']

    def validate_project(self, value):
        if value.status != 'active':
            raise serializers.ValidationError("Cannot report bugs for inactive projects.")
        return value
