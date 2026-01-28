from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import BugReport, BugAttachment, BugComment
from .serializers import BugReportSerializer, BugAttachmentSerializer, BugCommentSerializer
from .permissions import IsReportOwnerOrMaintainer, IsMaintainerOfProject, IsTester

@extend_schema_view(
    list=extend_schema(description="List bug reports for the user (Maintainer sees theirs, Tester sees theirs)", tags=['Bug Reporting']),
    create=extend_schema(description="Create a new bug report (Testers only)", tags=['Bug Reporting']),
    retrieve=extend_schema(description="Get a specific bug report", tags=['Bug Reporting']),
    update=extend_schema(description="Update a bug report (Owner or Maintainer)", tags=['Bug Reporting']),
    partial_update=extend_schema(description="Partially update a bug report", tags=['Bug Reporting']),
    destroy=extend_schema(description="Delete a bug report", tags=['Bug Reporting'])
)
@extend_schema(tags=['Bug Reporting'])
class BugReportViewSet(viewsets.ModelViewSet):
    queryset = BugReport.objects.all()
    serializer_class = BugReportSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'category', 'severity', 'status']
    ordering_fields = ['created_at', 'severity', 'status']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            return [IsTester()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsReportOwnerOrMaintainer()]
        if self.action in ['approve', 'reject', 'resolve']:
            return [IsMaintainerOfProject()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = BugReport.objects.select_related('project', 'tester').prefetch_related(
            'attachments', 
            'comments', 
            'comments__user'
        )
        if user.role == 'maintainer':
            return queryset.filter(project__maintainer=user)
        if user.role == 'tester':
            return queryset.filter(tester=user)
        return queryset.all()

    def perform_create(self, serializer):
        serializer.save(tester=self.request.user)

    @extend_schema(
        request=None,
        responses={200: BugReportSerializer},
        description="Approve a bug report (Maintainers only)",
        tags=['Bug Reporting']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsMaintainerOfProject])
    def approve(self, request, pk=None):
        bug_report = self.get_object()
        if bug_report.status != 'pending':
            return Response({"error": "Only pending reports can be approved."}, status=status.HTTP_400_BAD_REQUEST)
        bug_report.status = 'approved'
        bug_report.save()

        # Award XP based on severity
        xp_map = {
            'critical': 100,
            'high': 50,
            'medium': 30,
            'low': 10
        }
        xp_amount = xp_map.get(bug_report.severity, 10)
        
        from gamification.models import XPTransaction
        XPTransaction.objects.create(
            user=bug_report.tester,
            amount=xp_amount,
            source='bug_report_approved',
            reference_id=bug_report.id
        )
        return Response(BugReportSerializer(bug_report).data)

    @extend_schema(
        request=None,
        responses={200: BugReportSerializer},
        description="Reject a bug report (Maintainers only)",
        tags=['Bug Reporting']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsMaintainerOfProject])
    def reject(self, request, pk=None):
        bug_report = self.get_object()
        if bug_report.status != 'pending':
            return Response({"error": "Only pending reports can be rejected."}, status=status.HTTP_400_BAD_REQUEST)
        bug_report.status = 'rejected'
        bug_report.save()
        return Response(BugReportSerializer(bug_report).data)

    @extend_schema(
        request=None,
        responses={200: BugReportSerializer},
        description="Mark a bug report as resolved (Maintainers only)",
        tags=['Bug Reporting']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsMaintainerOfProject])
    def resolve(self, request, pk=None):
        bug_report = self.get_object()
        if bug_report.status != 'approved':
            return Response({"error": "Only approved reports can be resolved."}, status=status.HTTP_400_BAD_REQUEST)
        bug_report.status = 'resolved'
        bug_report.save()
        return Response(BugReportSerializer(bug_report).data)

@extend_schema(tags=['Bug Reporting'])
class BugCommentViewSet(viewsets.ModelViewSet):
    queryset = BugComment.objects.all()
    serializer_class = BugCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@extend_schema(tags=['Bug Reporting'])
class BugAttachmentViewSet(viewsets.ModelViewSet):
    queryset = BugAttachment.objects.all()
    serializer_class = BugAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
