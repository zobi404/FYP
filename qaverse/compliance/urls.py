from django.urls import path
from .views import ComplianceAuditView

urlpatterns = [
    path('audit/', ComplianceAuditView.as_view(), name='compliance-audit'),
]
