from rest_framework import serializers
from projects.models import Project
from accounts.serializers import UserSerializer

class ProjectSerializer(serializers.ModelSerializer):
    maintainer = UserSerializer(read_only=True)
    total_bugs_reported = serializers.IntegerField(read_only=True)
    total_active_testers = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'maintainer', 'title', 'description', 'instructions', 'technology_stack', 
                  'testing_url', 'category', 'status', 'created_at', 'updated_at', 
                  'total_bugs_reported', 'total_active_testers']
        read_only_fields = ['id', 'maintainer', 'created_at', 'updated_at']
