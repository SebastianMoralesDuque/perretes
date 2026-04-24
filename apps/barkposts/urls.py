from django.urls import path
from .views import (
    BarkPostCreateAPI, BarkPostUpdateAPI, BarkPostDeleteAPI, BarkPostLikeAPI,
    BarkPostFeedAPI, BarkPostUserListAPI
)
from .views_search import SearchAPI

urlpatterns = [
    path('', BarkPostFeedAPI.as_view(), name='barkpost-feed'),
    path('search/', SearchAPI.as_view(), name='search'),
    path('create/', BarkPostCreateAPI.as_view(), name='barkpost-create'),
    path('<int:barkpost_id>/update/', BarkPostUpdateAPI.as_view(), name='barkpost-update'),
    path('<int:barkpost_id>/delete/', BarkPostDeleteAPI.as_view(), name='barkpost-delete'),
    path('<int:barkpost_id>/like/', BarkPostLikeAPI.as_view(), name='barkpost-like'),
    path('user/<str:username>/', BarkPostUserListAPI.as_view(), name='barkpost-user-list'),
]
