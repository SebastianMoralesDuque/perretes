from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .services.user_service import user_create, user_authenticate_and_login
from .selectors.user_selector import user_get_by_username


class UserRegisterAPI(APIView):
    """Endpoint para registro de usuarios con auto-login."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = user_create(**serializer.validated_data)
            # Auto-login tras registro
            user_authenticate_and_login(
                request=request,
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            return Response(
                {
                    'message': 'Usuario registrado correctamente.',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'avatar_choice': user.avatar_choice,
                        'avatar_emoji': user.avatar_emoji,
                        'avatar_color': user.avatar_color,
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'errors': {'general': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserLoginAPI(APIView):
    """Endpoint para login de usuarios."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = user_authenticate_and_login(
                request=request,
                **serializer.validated_data
            )
            return Response(
                {
                    'message': 'Login exitoso.',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'avatar_choice': user.avatar_choice,
                        'avatar_emoji': user.avatar_emoji,
                        'avatar_color': user.avatar_color,
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'errors': {'general': str(e)}},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserLogoutAPI(APIView):
    """Endpoint para logout de usuarios."""
    
    @method_decorator(login_required)
    def post(self, request):
        logout(request)
        return Response(
            {'message': 'Logout exitoso.'},
            status=status.HTTP_200_OK
        )


class UserProfileAPI(APIView):
    """Endpoint para obtener datos de perfil de un usuario."""
    
    def get(self, request, username):
        user = user_get_by_username(username=username)
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'date_joined': user.date_joined,
                'avatar_choice': user.avatar_choice,
                'avatar_emoji': user.avatar_emoji,
                'avatar_color': user.avatar_color,
                'is_me': request.user.is_authenticated and request.user.id == user.id,
            },
            status=status.HTTP_200_OK
        )


class UserMeAPI(APIView):
    """Endpoint para obtener el usuario autenticado actual."""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'authenticated': False},
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'avatar_choice': request.user.avatar_choice,
                    'avatar_emoji': request.user.avatar_emoji,
                    'avatar_color': request.user.avatar_color,
                }
            },
            status=status.HTTP_200_OK
        )
