from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from projects.models import Project

class ProjectTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.projects_url = '/api/v1/projects/'
        
        # Create Maintainer
        self.maintainer = User.objects.create_user(
            email='maintainer@example.com', password='password123', role='maintainer'
        )
        
        # Create Tester
        self.tester = User.objects.create_user(
            email='tester@example.com', password='password123', role='tester'
        )
        
        # Create Project
        self.project_data = {
            'title': 'Test Project',
            'description': 'A test project description',
            'technology_stack': 'Django, React',
            'testing_url': 'http://example.com',
            'category': 'web'
        }

    def test_create_project_maintainer(self):
        self.client.force_authenticate(user=self.maintainer)
        response = self.client.post(self.projects_url, self.project_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().maintainer, self.maintainer)

    def test_create_project_tester_denied(self):
        self.client.force_authenticate(user=self.tester)
        response = self.client.post(self.projects_url, self.project_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 0)

    def test_list_projects(self):
        # Create a project first
        Project.objects.create(maintainer=self.maintainer, **self.project_data)
        
        # Unauthenticated request
        self.client.logout()
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_pagination(self):
        # Create 15 projects
        for i in range(15):
            Project.objects.create(maintainer=self.maintainer, **self.project_data)
            
        response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 15)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), 10)

    def test_update_project_owner(self):
        project = Project.objects.create(maintainer=self.maintainer, **self.project_data)
        self.client.force_authenticate(user=self.maintainer)
        
        update_data = {'title': 'Updated Title'}
        response = self.client.patch(f'{self.projects_url}{project.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_update_project_not_owner_denied(self):
        project = Project.objects.create(maintainer=self.maintainer, **self.project_data)
        other_maintainer = User.objects.create_user(
            email='other@example.com', password='password123', role='maintainer'
        )
        self.client.force_authenticate(user=other_maintainer)
        
        update_data = {'title': 'Hacked Title'}
        response = self.client.patch(f'{self.projects_url}{project.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_performance(self):
        # Create 20 projects with different maintainers to trigger N+1 if not optimized
        for i in range(20):
            maintainer = User.objects.create_user(email=f'm{i}@example.com', password='pw')
            Project.objects.create(maintainer=maintainer, **self.project_data)
        
        self.client.force_authenticate(user=self.maintainer)
        
        # Should be constant queries: 
        # 1 for user, 1 for session/auth (maybe), 1 for count, 1 for projects+maintainers
        # exact number depends on auth and other middleware, but should NOT be 20+
        with self.assertNumQueries(lambda n: n < 10): 
            response = self.client.get(self.projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
