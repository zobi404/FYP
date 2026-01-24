from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from django.db.models import Sum, Count
from drf_spectacular.utils import extend_schema
from accounts.models import User
from .models import XPTransaction, Badge, UserBadge
from .serializers import (
    XPTransactionSerializer, BadgeSerializer, 
    UserBadgeSerializer, LeaderboardSerializer
)

class XPTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = XPTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return XPTransaction.objects.filter(user=self.request.user).order_by('-timestamp')

class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user).order_by('-earned_at')

class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(tags=['Gamification'])
    def list(self, request, *args, **kwargs):
        # Annotate users with total XP and badges count
        queryset = User.objects.filter(role='tester').annotate(
            total_xp=Sum('xp_transactions__amount'),
            badges_count=Count('badges', distinct=True)
        ).filter(total_xp__isnull=False).order_by('-total_xp')[:50]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
