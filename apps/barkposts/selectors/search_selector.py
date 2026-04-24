from django.contrib.auth import get_user_model
from apps.barkposts.models import BarkPost

User = get_user_model()


def search_users(*, query: str, limit: int = 5):
    """Busca usuarios por username (case-insensitive)."""
    if not query or len(query) < 2:
        return []
    return User.objects.filter(
        username__icontains=query
    ).values('id', 'username')[:limit]


def search_posts(*, query: str, limit: int = 5):
    """Busca ladridos por contenido (case-insensitive)."""
    if not query or len(query) < 2:
        return []
    return BarkPost.objects.filter(
        content__icontains=query
    ).select_related('user').values('id', 'content', 'user__username')[:limit]
