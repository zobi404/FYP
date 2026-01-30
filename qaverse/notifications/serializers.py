from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source='actor.email', read_only=True)
    object_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'actor_email', 'verb', 'target_object_id', 'is_read', 'created_at', 'object_name']
        read_only_fields = ['id', 'actor_email', 'verb', 'target_object_id', 'created_at']

    def get_object_name(self, obj):
        if obj.target:
            if hasattr(obj.target, 'title'):
                return obj.target.title
            return str(obj.target)
        return None
