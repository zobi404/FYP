from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiTypes
from rest_framework import serializers

from .serializers import LoginSerializer, RegisterSerializer, UserSerializer, RefreshTokenSerializer

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
        return Response(
            {"message": "User registered successfully"},
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
        