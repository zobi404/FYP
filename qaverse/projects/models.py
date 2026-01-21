from django.db import models
from accounts.models import User

class Project(models.Model):
    CATEGORY_CHOICES = (
        ('web', 'Web'),
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    )

    maintainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    technology_stack = models.CharField(max_length=200, help_text="e.g. Django, React, PostgreSQL")
    testing_url = models.URLField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
