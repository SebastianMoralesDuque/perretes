from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .selectors.search_selector import search_users, search_posts


class SearchAPI(APIView):
    """
    Endpoint de búsqueda en tiempo real.
    Busca usuarios por username y ladridos por contenido.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        q = request.GET.get('q', '').strip()
        if len(q) < 2:
            return Response(
                {'users': [], 'posts': []},
                status=status.HTTP_200_OK
            )

        users = search_users(query=q)
        posts = search_posts(query=q)

        return Response(
            {
                'users': [
                    {'id': u['id'], 'username': u['username']}
                    for u in users
                ],
                'posts': [
                    {
                        'id': p['id'],
                        'content': p['content'],
                        'username': p['user__username'],
                    }
                    for p in posts
                ],
            },
            status=status.HTTP_200_OK
        )
