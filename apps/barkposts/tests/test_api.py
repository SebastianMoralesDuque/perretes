"""
test_api.py — Tests de integración HTTP para el módulo de barkposts.

Estrategia:
- APIClient simula requests reales contra el stack completo.
- Verificamos status codes, estructura de respuesta, y efectos
  colaterales en la base de datos.
- Mockeamos tareas Celery para no depender de infraestructura.
"""

import pytest

pytestmark = [pytest.mark.api]

import pytest
from django.urls import reverse
from unittest.mock import patch

from apps.barkposts.models import BarkPost, Like
from apps.barkposts.tests.factories import BarkPostFactory, LikeFactory
from apps.users.tests.factories import UserFactory


# ═══════════════════════════════════════════════
# Crear ladrido
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostCreateAPI:
    """Suite para POST /api/barkposts/create/"""

    @patch('apps.barkposts.views.barkpost_create')
    def test_crea_bark_autenticado(self, mock_create, authenticated_client):
        """
        Dado un usuario autenticado,
        cuando hago POST con contenido válido,
        entonces creo el ladrido y retorno 201.
        """
        # La view llama al service; testeamos la integración completa
        # pero mockamos el service para testear solo el contrato view→service
        mock_bark = BarkPostFactory()
        mock_create.return_value = mock_bark

        response = authenticated_client.post(
            reverse('barkpost-create'),
            data={'content': 'Mi primer ladrido!'},
            format='json',
        )

        assert response.status_code == 201
        assert 'barkpost' in response.data

    def test_rechaza_creacion_si_no_autenticado(self, api_client):
        """
        Dado un visitante anónimo,
        cuando hago POST a create,
        entonces retorno 403 (IsAuthenticatedOrReadOnly).
        """
        response = api_client.post(
            reverse('barkpost-create'),
            data={'content': 'Hackeo'},
            format='json',
        )

        assert response.status_code == 403

    def test_rechaza_contenido_vacio(self, authenticated_client):
        """
        Dado un usuario autenticado,
        cuando envío contenido vacío o solo espacios,
        entonces retorno 400.
        """
        response = authenticated_client.post(
            reverse('barkpost-create'),
            data={'content': '   '},
            format='json',
        )

        assert response.status_code == 400

    def test_rechaza_contenido_mayor_140_chars(self, authenticated_client):
        """
        Dado un usuario autenticado,
        cuando envío más de 140 caracteres,
        entonces retorno 400 con error de max_length.
        """
        response = authenticated_client.post(
            reverse('barkpost-create'),
            data={'content': 'x' * 141},
            format='json',
        )

        assert response.status_code == 400

    def test_acepta_exactamente_140_chars(self, authenticated_client):
        """
        Dado un usuario autenticado,
        cuando envío exactamente 140 caracteres,
        entonces retorno 201 (límite válido).
        """
        response = authenticated_client.post(
            reverse('barkpost-create'),
            data={'content': 'x' * 140},
            format='json',
        )

        assert response.status_code == 201


# ═══════════════════════════════════════════════
# Feed global
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostFeedAPI:
    """Suite para GET /api/barkposts/"""

    def test_feed_retorna_lista_paginada(self, api_client):
        """
        Dado 5 ladridos en la BD,
        cuando consulto el feed,
        entonces retorno estructura paginada con results.
        """
        BarkPostFactory.create_batch(5)

        response = api_client.get(reverse('barkpost-feed'))

        assert response.status_code == 200
        assert 'results' in response.data
        assert len(response.data['results']) == 5

    def test_feed_anonimo_no_ve_is_liked_by_me(self, api_client):
        """
        Dado un visitante anónimo,
        cuando consulto el feed,
        entonces is_liked_by_me es False para todos.
        """
        BarkPostFactory()

        response = api_client.get(reverse('barkpost-feed'))

        assert response.data['results'][0]['is_liked_by_me'] is False

    def test_feed_autenticado_ve_sus_likes(self, authenticated_client):
        """
        Dado un usuario autenticado que dio like a un bark,
        cuando consulta el feed,
        entonces is_liked_by_me es True para ese bark.
        """
        user = authenticated_client._user
        bark = BarkPostFactory()
        LikeFactory(user=user, barkpost=bark)

        response = authenticated_client.get(reverse('barkpost-feed'))

        assert response.data['results'][0]['is_liked_by_me'] is True


# ═══════════════════════════════════════════════
# Perfil de usuario (lista de ladridos)
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostUserListAPI:
    """Suite para GET /api/barkposts/user/<username>/"""

    def test_retorna_barks_del_usuario_ordenados(self, api_client):
        """
        Dado un usuario con 2 ladridos y otro con 1,
        cuando consulto el perfil del primero,
        entonces retorno solo sus 2 barks ordenados.
        """
        user = UserFactory(username='publico')
        BarkPostFactory.create_batch(2, user=user)
        BarkPostFactory()  # De otro usuario

        response = api_client.get(
            reverse('barkpost-user-list', kwargs={'username': 'publico'})
        )

        assert response.status_code == 200
        assert len(response.data['results']) == 2

    def test_perfil_inexistente_retorna_404(self, api_client):
        """
        Dado un username que no existe,
        cuando consulto su lista de ladridos,
        entonces retorno 404.
        """
        response = api_client.get(
            reverse('barkpost-user-list', kwargs={'username': 'fantasma'})
        )

        assert response.status_code == 404


# ═══════════════════════════════════════════════
# Like
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostLikeAPI:
    """Suite para POST /api/barkposts/<id>/like/"""

    def test_da_like_a_bark(self, authenticated_client):
        """
        Dado un ladrido existente,
        cuando un usuario autenticado da like,
        entonces retorno 200 con is_liked=True y likes_count=1.
        """
        bark = BarkPostFactory()

        response = authenticated_client.post(
            reverse('barkpost-like', kwargs={'barkpost_id': bark.id})
        )

        assert response.status_code == 200
        assert response.data['is_liked'] is True
        assert response.data['likes_count'] == 1

    def test_quita_like_si_ya_existe(self, authenticated_client):
        """
        Dado un ladrido con like previo del usuario,
        cuando doy like de nuevo,
        entonces retorno 200 con is_liked=False y likes_count=0.
        """
        user = authenticated_client._user
        bark = BarkPostFactory()
        LikeFactory(user=user, barkpost=bark)

        response = authenticated_client.post(
            reverse('barkpost-like', kwargs={'barkpost_id': bark.id})
        )

        assert response.status_code == 200
        assert response.data['is_liked'] is False
        assert response.data['likes_count'] == 0

    def test_rechaza_like_si_no_autenticado(self, api_client):
        """
        Dado un visitante anónimo,
        cuando intenta dar like,
        entonces retorno 403.
        """
        bark = BarkPostFactory()

        response = api_client.post(
            reverse('barkpost-like', kwargs={'barkpost_id': bark.id})
        )

        assert response.status_code == 403


# ═══════════════════════════════════════════════
# Editar
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostUpdateAPI:
    """Suite para PATCH /api/barkposts/<id>/update/"""

    def test_edita_bark_propio(self, authenticated_client):
        """
        Dado un ladrido propio,
        cuando hago PATCH con nuevo contenido,
        entonces actualizo y retorno 200.
        """
        user = authenticated_client._user
        bark = BarkPostFactory(user=user, content='original')

        response = authenticated_client.patch(
            reverse('barkpost-update', kwargs={'barkpost_id': bark.id}),
            data={'content': 'editado'},
            format='json',
        )

        assert response.status_code == 200
        bark.refresh_from_db()
        assert bark.content == 'editado'

    def test_rechaza_edicion_bark_ajeno(self, authenticated_client):
        """
        Dado un ladrido de otro usuario,
        cuando intento editarlo,
        entonces retorno 403.
        """
        otro = UserFactory()
        bark = BarkPostFactory(user=otro)

        response = authenticated_client.patch(
            reverse('barkpost-update', kwargs={'barkpost_id': bark.id}),
            data={'content': 'hackeo'},
            format='json',
        )

        assert response.status_code == 403

    def test_rechaza_edicion_si_no_autenticado(self, api_client):
        """
        Dado un ladrido existente,
        cuando un anónimo intenta editarlo,
        entonces retorno 403.
        """
        bark = BarkPostFactory()

        response = api_client.patch(
            reverse('barkpost-update', kwargs={'barkpost_id': bark.id}),
            data={'content': 'nada'},
            format='json',
        )

        assert response.status_code == 403


# ═══════════════════════════════════════════════
# Eliminar
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostDeleteAPI:
    """Suite para DELETE /api/barkposts/<id>/delete/"""

    def test_elimina_bark_propio(self, authenticated_client):
        """
        Dado un ladrido propio,
        cuando hago DELETE,
        entonces borro el registro y retorno 200.
        """
        user = authenticated_client._user
        bark = BarkPostFactory(user=user)
        bark_id = bark.id

        response = authenticated_client.delete(
            reverse('barkpost-delete', kwargs={'barkpost_id': bark.id})
        )

        assert response.status_code == 200
        assert not BarkPost.objects.filter(id=bark_id).exists()

    def test_rechaza_eliminacion_bark_ajeno(self, authenticated_client):
        """
        Dado un ladrido de otro usuario,
        cuando intento borrarlo,
        entonces retorno 403.
        """
        otro = UserFactory()
        bark = BarkPostFactory(user=otro)

        response = authenticated_client.delete(
            reverse('barkpost-delete', kwargs={'barkpost_id': bark.id})
        )

        assert response.status_code == 403

    def test_rechaza_eliminacion_anonimo(self, api_client):
        """
        Dado un ladrido existente,
        cuando un anónimo intenta borrarlo,
        entonces retorno 403.
        """
        bark = BarkPostFactory()

        response = api_client.delete(
            reverse('barkpost-delete', kwargs={'barkpost_id': bark.id})
        )

        assert response.status_code == 403
