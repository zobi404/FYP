from django.db.models import Count
from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from projects.models import Project
from projects.serializers import ProjectSerializer
from projects.permissions import IsMaintainerOrReadOnly
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Projects'])
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().select_related('maintainer').annotate(
        total_bugs_reported=Count('bug_reports'),
        total_active_testers=Count('bug_reports__tester', distinct=True)
    )
    serializer_class = ProjectSerializer
    permission_classes = [IsMaintainerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'technology_stack', 'category']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(maintainer=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def maintained(self, request):
        projects = Project.objects.filter(maintainer=request.user).select_related('maintainer').annotate(
            total_bugs_reported=Count('bug_reports'),
            total_active_testers=Count('bug_reports__tester', distinct=True)
        ).order_by('-created_at')
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)
