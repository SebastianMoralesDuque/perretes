"""
URL configuration for perretes project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('registro/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('api/users/', include('apps.users.urls')),
    path('api/barkposts/', include('apps.barkposts.urls')),
    path('usuarios/<str:username>/', TemplateView.as_view(template_name='profile.html'), name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
