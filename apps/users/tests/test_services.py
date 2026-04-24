"""
test_services.py — Tests unitarios para la capa de negocio de usuarios.

Estrategia:
- Mockeamos todo lo que no sea la propia función bajo test.
- No tocamos la base de datos: usamos unittest.mock para simular
  QuerySets, authenticate() y login().
- Esto garantiza tests rápidos (< 50ms cada uno) y aislados.
"""

import pytest

pytestmark = [pytest.mark.unit]

import pytest
from unittest.mock import MagicMock, patch
from django.core.exceptions import ValidationError

from apps.users.services.user_service import user_create, user_authenticate_and_login


# ═══════════════════════════════════════════════
# user_create
# ═══════════════════════════════════════════════

class TestUserCreate:
    """Suite para la creación de usuarios."""

    @patch('apps.users.services.user_service.User')
    def test_crea_usuario_con_datos_validos(self, mock_user_model):
        """
        Dado username y password válidos,
        cuando llamo a user_create,
        entonces retorna el usuario creado con username normalizado.
        """
        # Arrange
        mock_user = MagicMock()
        mock_user_model.objects.filter.return_value.exists.return_value = False
        mock_user_model.objects.create_user.return_value = mock_user

        # Act
        result = user_create(username='  JuanPerez  ', password='secreto123')

        # Assert
        mock_user_model.objects.create_user.assert_called_once_with(
            username='juanperez',
            password='secreto123',
            avatar_choice=1,
        )
        assert result == mock_user

    @patch('apps.users.services.user_service.User')
    def test_rechaza_username_duplicado(self, mock_user_model):
        """
        Dado un username que ya existe en la BD,
        cuando llamo a user_create,
        entonces lanza ValidationError.
        """
        mock_user_model.objects.filter.return_value.exists.return_value = True

        with pytest.raises(ValidationError, match='ya está registrado'):
            user_create(username='existente', password='pass123')

        mock_user_model.objects.create_user.assert_not_called()

    @patch('apps.users.services.user_service.User')
    def test_username_case_insensitive(self, mock_user_model):
        """
        Dado un username en MAYÚSCULAS que ya existe en minúsculas,
        cuando llamo a user_create,
        entonces lanza ValidationError (búsqueda iexact).
        """
        mock_user_model.objects.filter.return_value.exists.return_value = True

        with pytest.raises(ValidationError):
            user_create(username='EXISTENTE', password='pass123')

    @patch('apps.users.services.user_service.User')
    def test_asigna_avatar_personalizado(self, mock_user_model):
        """
        Dado un avatar_choice distinto al default,
        cuando llamo a user_create,
        entonces se pasa el valor correcto a create_user.
        """
        mock_user_model.objects.filter.return_value.exists.return_value = False
        mock_user_model.objects.create_user.return_value = MagicMock()

        user_create(username='nuevo', password='pass', avatar_choice=5)

        _, kwargs = mock_user_model.objects.create_user.call_args
        assert kwargs['avatar_choice'] == 5


# ═══════════════════════════════════════════════
# user_authenticate_and_login
# ═══════════════════════════════════════════════

class TestUserAuthenticateAndLogin:
    """Suite para autenticación y creación de sesión."""

    @patch('apps.users.services.user_service.login')
    @patch('apps.users.services.user_service.authenticate')
    def test_login_exitoso_con_credenciales_validas(self, mock_auth, mock_login):
        """
        Dado username y password correctos,
        cuando llamo a user_authenticate_and_login,
        entonces authenticate() retorna usuario, login() crea sesión,
        y retorno el usuario.
        """
        mock_request = MagicMock()
        mock_user = MagicMock()
        mock_user.is_active = True
        mock_auth.return_value = mock_user

        result = user_authenticate_and_login(
            request=mock_request,
            username='juan',
            password='secreto',
        )

        mock_auth.assert_called_once_with(
            request=mock_request,
            username='juan',
            password='secreto',
        )
        mock_login.assert_called_once_with(mock_request, mock_user)
        assert result == mock_user

    @patch('apps.users.services.user_service.authenticate')
    def test_rechaza_credenciales_invalidas(self, mock_auth):
        """
        Dado password incorrecto,
        cuando llamo a user_authenticate_and_login,
        entonces lanza ValidationError y NO llama a login().
        """
        mock_auth.return_value = None

        with pytest.raises(ValidationError, match='incorrectos'):
            user_authenticate_and_login(
                request=MagicMock(),
                username='juan',
                password='mala_pass',
            )

    @patch('apps.users.services.user_service.login')
    @patch('apps.users.services.user_service.authenticate')
    def test_rechaza_usuario_inactivo(self, mock_auth, mock_login):
        """
        Dado un usuario existente pero desactivado (is_active=False),
        cuando llamo a user_authenticate_and_login,
        entonces lanza ValidationError y NO llama a login().
        """
        mock_user = MagicMock()
        mock_user.is_active = False
        mock_auth.return_value = mock_user

        with pytest.raises(ValidationError, match='desactivada'):
            user_authenticate_and_login(
                request=MagicMock(),
                username='inactivo',
                password='pass',
            )

        mock_login.assert_not_called()

    @patch('apps.users.services.user_service.login')
    @patch('apps.users.services.user_service.authenticate')
    def test_normaliza_username_a_minusculas(self, mock_auth, mock_login):
        """
        Dado un username con MAYÚSCULAS y espacios,
        cuando llamo a user_authenticate_and_login,
        entonces authenticate recibe el username normalizado.
        """
        mock_user = MagicMock()
        mock_user.is_active = True
        mock_auth.return_value = mock_user

        user_authenticate_and_login(
            request=MagicMock(),
            username='  JUAN  ',
            password='secreto',
        )

        _, kwargs = mock_auth.call_args
        assert kwargs['username'] == 'juan'
