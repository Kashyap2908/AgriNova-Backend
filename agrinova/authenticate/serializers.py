from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for handling user registration with standard User model fields.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(
        required=True,
        error_messages={'invalid': "Enter a valid email address."}
    )

    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'password', 
            'confirm_password'
        ]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, data):
        # Validate password matches confirm_password
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        # Pop confirm_password before creating model instance
        validated_data.pop('confirm_password')
        
        # User is created and password is hashed automatically by create_user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer to authenticate users using either Email OR Username.
    """
    username = serializers.CharField(required=True, help_text="Can be username or email")
    password = serializers.CharField(
        required=True, 
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        username_or_email = data.get('username')
        password = data.get('password')

        # Find the user by username or email
        user = None
        if '@' in username_or_email:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                username_or_email = user_obj.username

        # Authenticate using standard backend
        user = authenticate(username=username_or_email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials. Please check your username/email and password.")

        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive. Please contact support.")

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to represent standard user details along with FarmerProfile details.
    """
    profile_completed = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'date_joined',
            'profile_completed',
            'full_name',
            'phone',
            'language',
            'avatar'
        ]
        read_only_fields = fields

    def get_profile_completed(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.profile_completed
        return False

    def get_full_name(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.full_name
        return ""

    def get_phone(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.phone_number
        return ""

    def get_language(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.preferred_language
        return "English"

    def get_avatar(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.profile_photo.url)
            return obj.profile.profile_photo.url
        return None


from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        user = User.objects.filter(email__iexact=value).first()
        if not user:
            raise serializers.ValidationError("No account found with this email address.")
        return value.lower()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must consist of 6 numerical digits.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise serializers.ValidationError({"email": "No account found with this email address."})

        # Validate password using Django built-in validators
        try:
            validate_password(password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        data['user'] = user
        return data


