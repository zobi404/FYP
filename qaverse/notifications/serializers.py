from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source='actor.email', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'actor_email', 'verb', 'target_object_id', 'is_read', 'created_at']
        read_only_fields = ['id', 'actor_email', 'verb', 'target_object_id', 'created_at']
