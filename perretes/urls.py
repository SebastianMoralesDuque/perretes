"""
URL configuration for perretes project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('registro/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('api/users/', include('apps.users.urls')),
    path('api/barkposts/', include('apps.barkposts.urls')),
    path('usuarios/<str:username>/', TemplateView.as_view(template_name='profile.html'), name='profile'),
]

# Serve media files in all environments (production uses container volume)
# Note: static() returns [] when DEBUG=False, so we use serve directly
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
