import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role="tester", **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, role="admin", **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("tester", "Tester"),
        ("maintainer", "Maintainer"),
        ("admin", "Admin"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    fullname = models.CharField(max_length=50, blank=True, null=True, default="")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="tester")
    
    # Profile Fields
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True, help_text="URL to avatar image (e.g. Cloudinary)")
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
    
class EmailOTP(models.Model):
    PURPOSE_CHOICES = (
        ('PASSWORD_RESET', 'Password Reset'),
        ('ACCOUNT_ACTIVATION', 'Account Activation'),
    )
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='PASSWORD_RESET')

    def is_valid(self):
        # Valid if not used and created within last 10 minutes
        if self.is_used:
            return False
        return timezone.now() < self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.email} ({self.purpose}): {self.otp_code}"
    