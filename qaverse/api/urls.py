from django.urls import path, include

urlpatterns = [
    path('auth/', include("accounts.urls")),
    path('bugs/', include("bug_reports.urls")),
    path('gamification/', include("gamification.urls")),
    path('notifications/', include("notifications.urls")),
    path('analytics/', include("analytics.urls")),
    path('', include("projects.urls")),
    path('bugs/', include("bug_reports.urls")),
]