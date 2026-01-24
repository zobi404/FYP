from django.urls import path
from .views import TesterStatsView, ProjectStatsView

urlpatterns = [
    path('tester/', TesterStatsView.as_view(), name='tester-stats'),
    path('project/<int:project_id>/', ProjectStatsView.as_view(), name='project-stats'),
]
