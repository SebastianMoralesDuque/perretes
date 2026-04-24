from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BarkPost, Like

User = get_user_model()


class BarkPostCreateSerializer(serializers.Serializer):
    """Serializer para crear un nuevo ladrido."""
    content = serializers.CharField(
        max_length=140,
        trim_whitespace=True,
        error_messages={
            'blank': 'El contenido no puede estar vacío.',
            'max_length': 'Los ladridos no pueden superar los 140 caracteres.',
        }
    )
    image = serializers.ImageField(required=False, allow_empty_file=False)
    
    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('El contenido no puede estar vacío.')
        if len(value) > 140:
            raise serializers.ValidationError('Máximo 140 caracteres.')
        return value


class BarkPostUpdateSerializer(serializers.Serializer):
    """Serializer para editar un ladrido existente."""
    content = serializers.CharField(
        max_length=140,
        trim_whitespace=True,
        required=False,
    )
    image = serializers.ImageField(required=False, allow_empty_file=False)
    remove_image = serializers.BooleanField(required=False, default=False)
    
    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('El contenido no puede estar vacío.')
        if len(value) > 140:
            raise serializers.ValidationError('Máximo 140 caracteres.')
        return value
    
    def validate(self, attrs):
        if not attrs.get('content') and not attrs.get('image') and not attrs.get('remove_image'):
            raise serializers.ValidationError('Debes proporcionar al menos un campo para actualizar.')
        return attrs


class BarkPostListSerializer(serializers.ModelSerializer):
    """Serializer para listar ladridos con datos del usuario, likes, imagen y avatar."""
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    avatar_choice = serializers.IntegerField(source='user.avatar_choice', read_only=True)
    avatar_emoji = serializers.CharField(source='user.avatar_emoji', read_only=True)
    avatar_color = serializers.CharField(source='user.avatar_color', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked_by_me = serializers.BooleanField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = BarkPost
        fields = [
            'id', 'user_id', 'username', 'avatar_choice', 'avatar_emoji', 'avatar_color',
            'content', 'image_url', 'likes_count', 'is_liked_by_me', 'created_at', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class LikeToggleSerializer(serializers.Serializer):
    """Serializer para toggle de like."""
    barkpost_id = serializers.IntegerField(required=True)
