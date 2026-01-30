from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname', 'role', 'bio', 'avatar_url', 'github_url', 'linkedin_url']

class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"error": "Invalid email or password"})

        refresh = RefreshToken.for_user(user)
        
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }
        
class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['fullname', 'email', 'role', 'password', 'password2', 'bio', 'avatar_url', 'github_url', 'linkedin_url']
        extra_kwargs = {
            "password" : {"write_only": True}
        }
        
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  
        password = validated_data.pop('password')
        # User is inactive until email verification
        user = User.objects.create(is_active=False, **validated_data)
        user.set_password(password)  
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value

class PasswordResetVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, data):
        # We don't want to use get_object_or_404 here to keep error messages consistent/abstract if needed
        # But per requirements we validation otp+email
        from accounts.models import EmailOTP
        
        try:
            # Get the latest OTP for this email
            otp_obj = EmailOTP.objects.filter(email=data['email'], purpose='PASSWORD_RESET').latest('created_at')
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or Email")

        if otp_obj.otp_code != data['otp']:
             raise serializers.ValidationError("Invalid OTP")
        
        if not otp_obj.is_valid():
            raise serializers.ValidationError("OTP has expired or already been used")
        
        return data

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField()

    def validate(self, data):
        from accounts.models import EmailOTP
        try:
            otp_obj = EmailOTP.objects.filter(email=data['email'], purpose='PASSWORD_RESET').latest('created_at')
        except EmailOTP.DoesNotExist:
             raise serializers.ValidationError("Invalid request")

        if otp_obj.otp_code != data['otp']:
             raise serializers.ValidationError("Invalid OTP")
        
        if not otp_obj.is_valid():
             raise serializers.ValidationError("OTP has expired or already been used")

        return data
    
    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        
        # Mark OTP as used
        from accounts.models import EmailOTP
        otp_obj = EmailOTP.objects.filter(email=email, purpose='PASSWORD_RESET').latest('created_at')
        otp_obj.is_used = True
        otp_obj.save()
        
        return user

class AccountVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, data):
        from accounts.models import EmailOTP
        try:
            otp_obj = EmailOTP.objects.filter(email=data['email'], purpose='ACCOUNT_ACTIVATION').latest('created_at')
        except EmailOTP.DoesNotExist:
             raise serializers.ValidationError("Invalid request")

        if otp_obj.otp_code != data['otp']:
             raise serializers.ValidationError("Invalid OTP")
        
        if not otp_obj.is_valid():
             raise serializers.ValidationError("OTP has expired or already been used")
             
        return data
        
    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        user.is_active = True
        user.save()
        
        from accounts.models import EmailOTP
        otp_obj = EmailOTP.objects.filter(email=email, purpose='ACCOUNT_ACTIVATION').latest('created_at')
        otp_obj.is_used = True
        otp_obj.save()
        
        return user
