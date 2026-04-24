from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()


def user_get_by_username(*, username: str) -> User:
    """
    Obtiene un usuario por su username (case-insensitive).
    Lanza 404 si no existe.
    """
    return get_object_or_404(User, username__iexact=username)


def user_exists(*, username: str) -> bool:
    """Verifica si un usuario existe."""
    return User.objects.filter(username__iexact=username).exists()
