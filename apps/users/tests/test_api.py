"""
test_api.py — Tests de integración HTTP para el módulo de usuarios.

Estrategia:
- Usamos APIClient de DRF para simular requests reales.
- Cada test ejecuta el stack completo: URL routing → View →
  Serializer → Service → ORM → Response.
- Esto detecta errores de integración que un test unitario no
  capturaría (ej. serializer mal configurado, URL mal mapeada).
"""

import pytest

pytestmark = [pytest.mark.api]


import pytest
from django.urls import reverse

from apps.users.tests.factories import UserFactory


# ═══════════════════════════════════════════════
# Registro
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestUserRegisterAPI:
    """Suite para POST /api/users/register/"""

    def test_registro_exitoso_crea_usuario_y_loguea(self, api_client):
        """
        Dado username y password válidos,
        cuando hago POST a register,
        entonces creo usuario, inicio sesión, y retorno 201.
        """
        payload = {
            'username': 'nuevo_usuario',
            'password': 'PassSegura123!',
        }

        response = api_client.post(
            reverse('user-register'),
            data=payload,
            format='json',
        )

        assert response.status_code == 201
        assert response.data['user']['username'] == 'nuevo_usuario'
        # Auto-login: la sesión debe estar activa
        assert '_auth_user_id' in api_client.session

    def test_rechaza_username_duplicado(self, api_client):
        """
        Dado un username que ya existe,
        cuando intento registrarme con él,
        entonces retorno 400 con error específico.
        """
        UserFactory(username='ocupado')
        payload = {
            'username': 'ocupado',
            'password': 'PassSegura123!',
        }

        response = api_client.post(
            reverse('user-register'),
            data=payload,
            format='json',
        )

        assert response.status_code == 400
        assert 'username' in response.data['errors'] or 'general' in response.data['errors']

    def test_rechaza_password_debil(self, api_client):
        """
        Dado un password demasiado corto/simple,
        cuando intento registrarme,
        entonces retorno 400 con error de validación.
        """
        payload = {
            'username': 'nuevo',
            'password': '123',
        }

        response = api_client.post(
            reverse('user-register'),
            data=payload,
            format='json',
        )

        assert response.status_code == 400


# ═══════════════════════════════════════════════
# Login
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestUserLoginAPI:
    """Suite para POST /api/users/login/"""

    def test_login_exitoso_retorna_usuario(self, api_client):
        """
        Dado un usuario existente con password conocido,
        cuando hago POST a login con credenciales correctas,
        entonces retorno 200 y datos del usuario.
        """
        user = UserFactory(username='juan', password='testpass123')
        payload = {
            'username': 'juan',
            'password': 'testpass123',
        }

        response = api_client.post(
            reverse('user-login'),
            data=payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.data['user']['username'] == 'juan'
        assert '_auth_user_id' in api_client.session

    def test_login_falla_con_credenciales_invalidas(self, api_client):
        """
        Dado un usuario existente,
        cuando hago POST con password incorrecto,
        entonces retorno 401.
        """
        UserFactory(username='juan', password='correcta')
        payload = {
            'username': 'juan',
            'password': 'incorrecta',
        }

        response = api_client.post(
            reverse('user-login'),
            data=payload,
            format='json',
        )

        assert response.status_code == 401

    def test_login_falla_con_usuario_inexistente(self, api_client):
        """
        Dado que no existe el usuario,
        cuando hago POST a login,
        entonces retorno 401.
        """
        payload = {
            'username': 'fantasma',
            'password': 'cualquiera',
        }

        response = api_client.post(
            reverse('user-login'),
            data=payload,
            format='json',
        )

        assert response.status_code == 401


# ═══════════════════════════════════════════════
# Perfil
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestUserProfileAPI:
    """Suite para GET /api/users/<username>/profile/"""

    def test_perfil_existente_retorna_datos(self, api_client):
        """
        Dado un usuario público,
        cuando consulto su perfil,
        entonces retorno 200 con sus datos.
        """
        user = UserFactory(username='publico')

        response = api_client.get(
            reverse('user-profile', kwargs={'username': 'publico'})
        )

        assert response.status_code == 200
        assert response.data['username'] == 'publico'
        assert 'avatar_emoji' in response.data
        assert 'is_me' in response.data

    def test_perfil_inexistente_retorna_404(self, api_client):
        """
        Dado que no existe el usuario,
        cuando consulto su perfil,
        entonces retorno 404.
        """
        response = api_client.get(
            reverse('user-profile', kwargs={'username': 'no_existe'})
        )

        assert response.status_code == 404

    def test_is_me_true_para_usuario_autenticado(self, authenticated_client):
        """
        Dado un usuario autenticado consultando su propio perfil,
        cuando hago GET,
        entonces is_me es True.
        """
        username = authenticated_client._user.username

        response = authenticated_client.get(
            reverse('user-profile', kwargs={'username': username})
        )

        assert response.status_code == 200
        assert response.data['is_me'] is True

    def test_is_me_false_para_otro_usuario(self, authenticated_client):
        """
        Dado un usuario autenticado consultando perfil ajeno,
        cuando hago GET,
        entonces is_me es False.
        """
        UserFactory(username='otro')

        response = authenticated_client.get(
            reverse('user-profile', kwargs={'username': 'otro'})
        )

        assert response.status_code == 200
        assert response.data['is_me'] is False


# ═══════════════════════════════════════════════
# Me
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestUserMeAPI:
    """Suite para GET /api/users/me/"""

    def test_anonimo_retorna_authenticated_false(self, api_client):
        """
        Dado un visitante sin sesión,
        cuando consulto /me,
        entonces retorno 200 con authenticated=False.
        """
        response = api_client.get(reverse('user-me'))

        assert response.status_code == 200
        assert response.data['authenticated'] is False

    def test_autenticado_retorna_datos(self, authenticated_client):
        """
        Dado un usuario logueado,
        cuando consulto /me,
        entonces retorno 200 con authenticated=True y datos del user.
        """
        response = authenticated_client.get(reverse('user-me'))

        assert response.status_code == 200
        assert response.data['authenticated'] is True
        assert 'username' in response.data['user']
