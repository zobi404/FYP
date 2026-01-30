from rest_framework import views, permissions, response
from django.db.models import Count, Sum, Q
from drf_spectacular.utils import extend_schema
from bug_reports.models import BugReport
from gamification.models import XPTransaction
from projects.models import Project
from .serializers import TesterStatsSerializer, ProjectStatsSerializer, MaintainerStatsSerializer

class TesterStatsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=TesterStatsSerializer, tags=['Analytics'])
    def get(self, request):
        user = request.user
        total_xp = XPTransaction.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
        bug_reports = BugReport.objects.filter(tester=user)
        total_bugs = bug_reports.count()
        approved_bugs = bug_reports.filter(status='approved').count()
        
        success_rate = (approved_bugs / total_bugs * 100) if total_bugs > 0 else 0
        
        data = {
            'email': user.email,
            'total_xp': total_xp,
            'bug_reports_count': total_bugs,
            'approved_bugs_count': approved_bugs,
            'success_rate': round(success_rate, 2)
        }
        return response.Response(data)

class ProjectStatsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=ProjectStatsSerializer, tags=['Analytics'])
    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return response.Response({'error': 'Project not found'}, status=404)
        
        bug_reports = BugReport.objects.filter(project=project)
        total_bugs = bug_reports.count()
        
        status_dist = bug_reports.values('status').annotate(count=Count('status'))
        severity_dist = bug_reports.values('severity').annotate(count=Count('severity'))
        
        data = {
            'project_title': project.title,
            'total_bugs': total_bugs,
            'status_distribution': {item['status']: item['count'] for item in status_dist},
            'severity_distribution': {item['severity']: item['count'] for item in severity_dist}
        }
        return response.Response(data)

class MaintainerStatsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=MaintainerStatsSerializer, tags=['Analytics'])
    def get(self, request):
        user = request.user
        
        # 1. Active Projects of maintainer
        active_projects = Project.objects.filter(maintainer=user, status='active').count()
        
        # 2. Total testers testing on maintainer projects
        # Testers who have submitted at least one bug report on any project owned by the maintainer
        testers_count = BugReport.objects.filter(project__maintainer=user).values('tester').distinct().count()
        
        # 3. Total bug reports for this maintainer
        total_bugs = BugReport.objects.filter(project__maintainer=user).count()
        
        # 4. Total approved bugs
        approved_bugs = BugReport.objects.filter(project__maintainer=user, status='approved').count()
        
        data = {
            'total_active_projects': active_projects,
            'total_testers': testers_count,
            'total_bugs': total_bugs,
            'approved_bugs': approved_bugs
        }
        return response.Response(data)
