from django.urls import path
from .views import TesterStatsView, ProjectStatsView, MaintainerStatsView

urlpatterns = [
    path('tester/', TesterStatsView.as_view(), name='tester-stats'),
    path('project/<int:project_id>/', ProjectStatsView.as_view(), name='project-stats'),
    path('maintainer/', MaintainerStatsView.as_view(), name='maintainer-stats'),
]
