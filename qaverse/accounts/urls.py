from django.urls import path
from .views import (
    Login, Register, GetNewAccessToken, ProtectedView, ProfileView,
    ChangePasswordView, PasswordResetRequestView, PasswordResetVerifyView,
    PasswordResetConfirmView, VerifyAccountView
)

urlpatterns = [
    path('login/', Login.as_view()),
    path('register/', Register.as_view()),
    path('refresh-token/', GetNewAccessToken.as_view()),
    path('authenticated-route/', ProtectedView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path('password-reset/request/', PasswordResetRequestView.as_view()),
    path('password-reset/verify/', PasswordResetVerifyView.as_view()),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view()),
    path('verify-account/', VerifyAccountView.as_view()),
]