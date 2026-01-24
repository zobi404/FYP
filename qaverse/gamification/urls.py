from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import XPTransactionViewSet, BadgeViewSet, UserBadgeViewSet, LeaderboardViewSet

router = DefaultRouter()
router.register(r'transactions', XPTransactionViewSet, basename='xptransaction')
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'my-badges', UserBadgeViewSet, basename='userbadge')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')

urlpatterns = [
    path('', include(router.urls)),
]
