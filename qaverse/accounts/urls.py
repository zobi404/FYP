from django.urls import path
from .views import Login, Register, GetNewAccessToken, ProtectedView, ProfileView

urlpatterns = [
    path('login/', Login.as_view()),
    path('register/', Register.as_view()),
    path('refresh-token/', GetNewAccessToken.as_view()),
    path('authenticated-route/', ProtectedView.as_view()),
    path('profile/', ProfileView.as_view()),
    
]