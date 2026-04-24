from django.db import models
from django.conf import settings


class BarkPost(models.Model):
    """Modelo para los 'ladridos' (mensajes cortos de la red social)."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='barkposts',
        db_index=True,
    )
    content = models.CharField(
        max_length=140,
        help_text='Máximo 140 caracteres.',
    )
    image = models.ImageField(
        upload_to='barkposts/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text='Imagen opcional adjunta al ladrido.',
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'barkposts_barkpost'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f'@{self.user.username}: {self.content[:50]}...'


class Like(models.Model):
    """Modelo para los 'likes' de un ladrido."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        db_index=True,
    )
    barkpost = models.ForeignKey(
        BarkPost,
        on_delete=models.CASCADE,
        related_name='likes',
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'barkposts_like'
        unique_together = ['user', 'barkpost']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} likes {self.barkpost.id}'
