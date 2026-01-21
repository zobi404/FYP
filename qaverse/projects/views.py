from rest_framework import viewsets, filters    
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from projects.models import Project
from projects.serializers import ProjectSerializer
from projects.permissions import IsMaintainerOrReadOnly

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsMaintainerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'technology_stack', 'category']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(maintainer=self.request.user)
