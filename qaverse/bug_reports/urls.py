from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BugReportViewSet, BugCommentViewSet, BugAttachmentViewSet

router = DefaultRouter()
router.register(r'reports', BugReportViewSet, basename='bugreport')
router.register(r'comments', BugCommentViewSet, basename='bugcomment')
router.register(r'attachments', BugAttachmentViewSet, basename='bugattachment')

urlpatterns = [
    path('', include(router.urls)),
]
