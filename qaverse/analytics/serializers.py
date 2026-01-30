from rest_framework import serializers

class TesterStatsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    total_xp = serializers.IntegerField()
    bug_reports_count = serializers.IntegerField()
    approved_bugs_count = serializers.IntegerField()
    success_rate = serializers.FloatField()

class ProjectStatsSerializer(serializers.Serializer):
    project_title = serializers.CharField()
    total_bugs = serializers.IntegerField()
    status_distribution = serializers.DictField()
    severity_distribution = serializers.DictField()

class MaintainerStatsSerializer(serializers.Serializer):
    total_active_projects = serializers.IntegerField()
    total_testers = serializers.IntegerField()
    total_bugs = serializers.IntegerField()
    approved_bugs = serializers.IntegerField()
