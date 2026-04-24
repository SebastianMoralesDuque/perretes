from django.urls import path
from .views import UserRegisterAPI, UserLoginAPI, UserLogoutAPI, UserProfileAPI, UserMeAPI

urlpatterns = [
    path('register/', UserRegisterAPI.as_view(), name='user-register'),
    path('login/', UserLoginAPI.as_view(), name='user-login'),
    path('logout/', UserLogoutAPI.as_view(), name='user-logout'),
    path('me/', UserMeAPI.as_view(), name='user-me'),
    path('<str:username>/profile/', UserProfileAPI.as_view(), name='user-profile'),
]
