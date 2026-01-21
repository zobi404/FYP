from rest_framework import serializers
from projects.models import Project
from accounts.serializers import UserSerializer

class ProjectSerializer(serializers.ModelSerializer):
    maintainer = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'maintainer', 'title', 'description', 'technology_stack', 
                  'testing_url', 'category', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'maintainer', 'created_at', 'updated_at']
