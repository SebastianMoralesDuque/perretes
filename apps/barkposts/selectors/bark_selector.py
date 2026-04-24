from django.db import models
from django.db.models import QuerySet, Count, Exists, OuterRef
from apps.barkposts.models import BarkPost, Like


def _annotate_likes(queryset, user) -> QuerySet:
    """Annota likes_count e is_liked_by_me a un queryset de BarkPost."""
    queryset = queryset.annotate(likes_count=Count('likes'))
    if user and user.is_authenticated:
        queryset = queryset.annotate(
            is_liked_by_me=Exists(
                Like.objects.filter(barkpost_id=OuterRef('pk'), user=user)
            )
        )
    else:
        queryset = queryset.annotate(is_liked_by_me=models.Value(False, output_field=models.BooleanField()))
    return queryset


def barkpost_list_all(*, user=None) -> QuerySet:
    """
    Retorna todos los ladridos ordenados por fecha descendente.
    Usa select_related para evitar N+1 al acceder a user.username.
    """
    queryset = BarkPost.objects.select_related('user').order_by('-created_at')
    return _annotate_likes(queryset, user)


def barkpost_list_by_user(*, user_id: int, viewer=None) -> QuerySet:
    """
    Retorna los ladridos de un usuario específico.
    """
    queryset = BarkPost.objects.filter(user_id=user_id).select_related('user').order_by('-created_at')
    return _annotate_likes(queryset, viewer)


def barkpost_get_by_id(*, barkpost_id: int, viewer=None):
    """
    Obtiene un ladrido por ID con anotaciones de likes.
    """
    queryset = BarkPost.objects.filter(id=barkpost_id).select_related('user')
    queryset = _annotate_likes(queryset, viewer)
    return queryset.first()


def barkpost_is_liked_by_user(*, user_id: int, barkpost_id: int) -> bool:
    """Verifica si un usuario ha dado like a un ladrido."""
    return Like.objects.filter(user_id=user_id, barkpost_id=barkpost_id).exists()
