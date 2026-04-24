from django.contrib import admin
from .models import BarkPost, Like


@admin.register(BarkPost)
class BarkPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_preview', 'has_image', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['content', 'user__username']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenido'
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Imagen'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'barkpost', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'barkpost__content']
    date_hierarchy = 'created_at'
