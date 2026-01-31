from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiTypes
from rest_framework import serializers

from .serializers import (
    LoginSerializer, RegisterSerializer, UserSerializer, RefreshTokenSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer, 
    PasswordResetVerifySerializer, PasswordResetConfirmSerializer, AccountVerificationSerializer
)

class Login(GenericAPIView):
    serializer_class = LoginSerializer

    @extend_schema(
        tags=['Auth'],
        responses={
            200: inline_serializer(
                name='LoginResponse',
                fields={
                    'refresh': serializers.CharField(),
                    'access': serializers.CharField(),
                    'user': UserSerializer(),
                }
            )
        }
    )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class GetNewAccessToken(GenericAPIView):
    serializer_class = RefreshTokenSerializer

    @extend_schema(
        tags=['Auth'],
        responses={
            200: inline_serializer(
                name='RefreshTokenResponse',
                fields={
                    'message': serializers.CharField(),
                    'access_token': serializers.CharField(),
                }
            ),
            400: inline_serializer(
                name='RefreshTokenError',
                fields={
                    'error': serializers.CharField(),
                    'details': serializers.CharField(), # Or DictField/ListField depending on serializer.errors
                }
            )
        }
    )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
             return Response(
                {"error": "Invalid or missing refresh token", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            new_token = RefreshToken(serializer.validated_data['refresh_token'])
            return Response(
                {"message": "Access Token Refreshed Successfully",
                 "access_token": str(new_token.access_token)},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Invalid or missing refresh token", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class Register(GenericAPIView):
    serializer_class = RegisterSerializer

    @extend_schema(
        tags=['Auth'],
        responses={
            201: inline_serializer(
                name='RegisterResponse',
                fields={
                    'message': serializers.CharField(),
                }
            )
        }
    )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate OTP
        import random
        otp_code = str(random.randint(100000, 999999))
        
        from accounts.models import EmailOTP
        EmailOTP.objects.create(email=user.email, otp_code=otp_code, purpose='ACCOUNT_ACTIVATION')
        
        # Send Email
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        
        subject = 'Verify Your Account - Qaverse'
        html_message = render_to_string('accounts/account_verification_email.html', {'otp_code': otp_code})
        plain_message = strip_tags(html_message)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        
        try:
            send_mail(subject, plain_message, email_from, recipient_list, html_message=html_message, fail_silently=False)
        except Exception as e:
            # Delete user if email fails to avoid stale accounts
            user.delete()
            return Response(
                {"error": "Failed to send verification email", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "User registered successfully. Please verify your email."},
            status=status.HTTP_201_CREATED
        )
        
class ProtectedView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        tags=['Auth'],
        responses={
            200: inline_serializer(
                name='ProtectedResponse',
                fields={
                    'message': serializers.CharField(),
                }
            )
        }
    )
    def get(self, request):
        return Response({"message": "Authenticated Request"})

class ProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(tags=['Auth'])
    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Auth'])
    def patch(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChangePasswordView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(tags=['Auth'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = []

    @extend_schema(tags=['Auth'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Generate OTP
        import random
        otp_code = str(random.randint(100000, 999999))
        
        from accounts.models import EmailOTP
        EmailOTP.objects.create(email=email, otp_code=otp_code, purpose='PASSWORD_RESET')
        
        # Send Email
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        
        subject = 'Password Reset Request - Qaverse'
        html_message = render_to_string('accounts/password_reset_email.html', {'otp_code': otp_code})
        plain_message = strip_tags(html_message)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        send_mail(subject, plain_message, email_from, recipient_list, html_message=html_message, fail_silently=False)
        
        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)

class PasswordResetVerifyView(GenericAPIView):
    serializer_class = PasswordResetVerifySerializer
    permission_classes = []

    @extend_schema(tags=['Auth'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = []

    @extend_schema(tags=['Auth'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

class VerifyAccountView(GenericAPIView):
    serializer_class = AccountVerificationSerializer
    permission_classes = []

    @extend_schema(tags=['Auth'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Account verified successfully"}, status=status.HTTP_200_OK)
        