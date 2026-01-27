from rest_framework import serializers
from django.db.models import Sum
from .models import XPTransaction, Badge, UserBadge
from accounts.models import User

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon_url', 'xp_required']

class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'earned_at']

class XPTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPTransaction
        fields = ['id', 'amount', 'source', 'reference_id', 'timestamp']

class LeaderboardSerializer(serializers.ModelSerializer):
    total_xp = serializers.IntegerField()
    badges_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname', 'role', 'total_xp', 'badges_count']
