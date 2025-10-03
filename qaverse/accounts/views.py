from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, RegisterSerializer

class Login(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class GetNewAccessToken(GenericAPIView):
    
    def post(self, request, *args, **kwargs):
        try:
            new_token = RefreshToken(request.data['refresh_token'])
            return Response(
                {"message": "Access Token Refreshed Successfully",
                 "access_token": str(new_token.access_token)},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            raise Exception(f"Invalid refresh token: {e}")

class Register(GenericAPIView):
    serializer_class = RegisterSerializer

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
    def get(self, request):
        return Response({"message": "Authenticated Request"})
        