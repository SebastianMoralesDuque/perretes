from django.db import models
from django.contrib.auth.models import AbstractUser


AVATAR_CHOICES = [
    (1, '🐶'),
    (2, '🐱'),
    (3, '🦊'),
    (4, '🐼'),
    (5, '🐨'),
    (6, '🐯'),
    (7, '🦁'),
    (8, '🐰'),
]

AVATAR_COLORS = {
    1: '#FF6B6B',
    2: '#4ECDC4',
    3: '#FF9F43',
    4: '#A29BFE',
    5: '#FD79A8',
    6: '#FDCB6E',
    7: '#6C5CE7',
    8: '#00B894',
}


class User(AbstractUser):
    """Extensión del usuario de Django con avatar predeterminado."""

    avatar_choice = models.PositiveSmallIntegerField(
        default=1,
        choices=AVATAR_CHOICES,
        help_text='Avatar predeterminado del usuario'
    )

    class Meta:
        db_table = 'auth_user'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username

    @property
    def avatar_emoji(self):
        return dict(AVATAR_CHOICES).get(self.avatar_choice, '🐶')

    @property
    def avatar_color(self):
        return AVATAR_COLORS.get(self.avatar_choice, '#FF6B6B')
