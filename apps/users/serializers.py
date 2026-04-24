from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer para registro de usuario con validaciones robustas."""
    username = serializers.CharField(
        max_length=150,
        trim_whitespace=True,
        error_messages={
            'blank': 'El nombre de usuario es obligatorio.',
            'max_length': 'El nombre de usuario no puede superar los 150 caracteres.',
        }
    )
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        error_messages={
            'blank': 'La contraseña es obligatoria.',
        }
    )
    avatar_choice = serializers.IntegerField(
        min_value=1,
        max_value=8,
        required=False,
        default=1
    )

    def validate_username(self, value):
        value = value.strip().lower()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya está en uso.')
        return value

    def validate(self, attrs):
        # Sanitización adicional
        attrs['username'] = attrs['username'].strip().lower()
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil público de usuario."""
    avatar_choice = serializers.IntegerField(source='avatar_choice', read_only=True)
    avatar_emoji = serializers.CharField(source='avatar_emoji', read_only=True)
    avatar_color = serializers.CharField(source='avatar_color', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'date_joined', 'avatar_choice', 'avatar_emoji', 'avatar_color']
        read_only_fields = fields


class UserLoginSerializer(serializers.Serializer):
    """Serializer para login de usuario."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
