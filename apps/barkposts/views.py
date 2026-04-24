from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from .serializers import (
    BarkPostCreateSerializer, BarkPostUpdateSerializer,
    BarkPostListSerializer, LikeToggleSerializer
)
from .services.bark_service import barkpost_create, barkpost_update, barkpost_delete, barkpost_like_toggle
from .selectors.bark_selector import barkpost_list_all, barkpost_list_by_user

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BarkPostCreateAPI(APIView):
    """Endpoint para crear un nuevo ladrido (con imagen opcional)."""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        serializer = BarkPostCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            bark = barkpost_create(
                user=request.user,
                content=serializer.validated_data['content'],
                image=serializer.validated_data.get('image')
            )
            return Response(
                {
                    'message': 'Ladrido publicado.',
                    'barkpost': BarkPostListSerializer(bark, context={'request': request}).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'errors': {'general': str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BarkPostUpdateAPI(APIView):
    """Endpoint para editar un ladrido propio (con imagen opcional)."""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def patch(self, request, barkpost_id):
        serializer = BarkPostUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            bark = barkpost_update(
                user=request.user,
                barkpost_id=barkpost_id,
                content=serializer.validated_data.get('content'),
                image=serializer.validated_data.get('image'),
                remove_image=serializer.validated_data.get('remove_image', False)
            )
            return Response(
                {
                    'message': 'Ladrido actualizado.',
                    'barkpost': BarkPostListSerializer(bark, context={'request': request}).data
                },
                status=status.HTTP_200_OK
            )
        except PermissionDenied as e:
            return Response(
                {'errors': {'general': str(e)}},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {'errors': {'general': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )


class BarkPostLikeAPI(APIView):
    """Endpoint para dar/quitar like a un ladrido."""
    
    def post(self, request, barkpost_id):
        try:
            result = barkpost_like_toggle(
                user=request.user,
                barkpost_id=barkpost_id
            )
            return Response(
                {
                    'message': 'Like actualizado.',
                    'likes_count': result['likes_count'],
                    'is_liked': result['is_liked'],
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'errors': {'general': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )


class BarkPostDeleteAPI(APIView):
    """Endpoint para eliminar un ladrido propio."""

    def delete(self, request, barkpost_id):
        try:
            barkpost_delete(user=request.user, barkpost_id=barkpost_id)
            return Response(
                {'message': 'Ladrido eliminado correctamente.'},
                status=status.HTTP_200_OK
            )
        except PermissionDenied as e:
            return Response(
                {'errors': {'general': str(e)}},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {'errors': {'general': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )


class BarkPostFeedAPI(APIView):
    """Endpoint para el feed global de ladridos (paginado)."""
    
    def get(self, request):
        queryset = barkpost_list_all(user=request.user if request.user.is_authenticated else None)
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = BarkPostListSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class BarkPostUserListAPI(APIView):
    """Endpoint para listar ladridos de un usuario específico (paginado)."""
    
    def get(self, request, username):
        user = get_object_or_404(User, username__iexact=username)
        queryset = barkpost_list_by_user(
            user_id=user.id,
            viewer=request.user if request.user.is_authenticated else None
        )
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = BarkPostListSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
