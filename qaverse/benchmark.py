import os
import django
import time
from django.db import connection, reset_queries
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qaverse.settings.base')
django.setup()

from accounts.models import User
from projects.models import Project
from bug_reports.models import BugReport, BugComment, BugAttachment
from notifications.models import Notification

def benchmark_queries():
    print("Setting up test data...")
    # Create Maintainer
    maintainer, _ = User.objects.get_or_create(email='perf_maintainer@example.com', role='maintainer')
    maintainer.set_password('password')
    maintainer.save()

    # Create Testers
    testers = []
    for i in range(5):
        t, _ = User.objects.get_or_create(email=f'perf_tester_{i}@example.com', role='tester')
        testers.append(t)

    # Create Projects
    for i in range(10):
        Project.objects.get_or_create(
            title=f'Perf Project {i}', 
            maintainer=maintainer,
            defaults={'category': 'web'}
        )
    
    # Create Bug Reports with related data
    project = Project.objects.first()
    for i in range(10):
        bug, _ = BugReport.objects.get_or_create(
            title=f'Perf Bug {i}',
            project=project,
            tester=testers[i % 5],
            defaults={'severity': 'high'}
        )
        BugComment.objects.create(bug_report=bug, user=maintainer, text="Fixing it")
        BugAttachment.objects.create(bug_report=bug, file_url="http://example.com/file.jpg")

    print("\n--- Benchmarking Projects List ---")
    reset_queries()
    projects = list(Project.objects.all().select_related('maintainer'))
    # Simulate serialization access
    for p in projects:
        _ = p.maintainer.email
    
    print(f"Projects Count: {len(projects)}")
    print(f"Query Count: {len(connection.queries)}")
    if len(connection.queries) > 5:
        print("WARNING: Project queries seem high!")
    else:
        print("SUCCESS: Project queries optimized.")

    print("\n--- Benchmarking Bug Reports List ---")
    reset_queries()
    # Use the optimized queryset logic from view
    bugs = list(BugReport.objects.select_related('project', 'tester').prefetch_related(
            'attachments', 'comments', 'comments__user'
        ).all())
    
    for b in bugs:
        _ = b.project.title
        _ = b.tester.email
        _ = [c.user.email for c in b.comments.all()]
        _ = [a.file_url for a in b.attachments.all()]

    print(f"Bug Reports Count: {len(bugs)}")
    print(f"Query Count: {len(connection.queries)}")
    # 1 main + 1 attachments + 1 comments + 1 comments__user = ~4 queries
    if len(connection.queries) > 6: 
        print("WARNING: Bug Report queries seem high!")
    else:
        print(f"SUCCESS: Bug Report queries optimized ({len(connection.queries)}).")

if __name__ == "__main__":
    try:
        benchmark_queries()
    except Exception as e:
        import traceback
        traceback.print_exc()
