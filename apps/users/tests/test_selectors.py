"""
test_selectors.py — Tests para los selectores (queries encapsuladas) de users.

Nota técnica:
- Los selectores acceden a la base de datos, por lo que estos tests
  SÍ requieren `@pytest.mark.django_db`.
- No son "puramente unitarios" en sentido estricto (toca I/O),
  pero son rápidos (< 100ms) porque usan SQLite in-memory.
- Testeamos comportamiento real del ORM: case-insensitive lookups,
  ordenamientos, y excepciones.
"""

import pytest

pytestmark = [pytest.mark.integration]

from django.http import Http404

from apps.users.selectors.user_selector import user_get_by_username, user_exists
from apps.users.tests.factories import UserFactory


# ═══════════════════════════════════════════════
# user_get_by_username
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestUserGetByUsername:
    """Suite para búsqueda de usuario por username."""

    def test_retorna_usuario_existente(self):
        """
        Dado un usuario con username 'pedrito',
        cuando busco por 'pedrito',
        entonces retorno la instancia correcta.
        """
        user = UserFactory(username='pedrito')

        result = user_get_by_username(username='pedrito')

        assert result == user
        assert result.username == 'pedrito'

    def test_busqueda_case_insensitive(self):
        """
        Dado un usuario 'Maria',
        cuando busco por 'MARIA' o 'maria',
        entonces lo encuentra igual (iexact).
        """
        user = UserFactory(username='Maria')

        assert user_get_by_username(username='MARIA') == user
        assert user_get_by_username(username='maria') == user
        assert user_get_by_username(username='MaRiA') == user

    def test_lanza_404_si_no_existe(self):
        """
        Dado que no existe ningún usuario 'fantasma',
        cuando busco por ese username,
        entonces lanza Http404.
        """
        with pytest.raises(Http404):
            user_get_by_username(username='fantasma')


# ═══════════════════════════════════════════════
# user_exists
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestUserExists:
    """Suite para verificación de existencia de usuario."""

    def test_retorna_true_si_existe(self):
        """
        Dado un usuario existente,
        cuando pregunto si existe,
        entonces retorna True.
        """
        UserFactory(username='existente')

        assert user_exists(username='existente') is True

    def test_retorna_false_si_no_existe(self):
        """
        Dado que no existe el usuario,
        cuando pregunto si existe,
        entonces retorna False.
        """
        assert user_exists(username='inexistente') is False

    def test_case_insensitive(self):
        """
        Dado un usuario 'Carlos',
        cuando pregunto por 'CARLOS',
        entonces retorna True.
        """
        UserFactory(username='Carlos')

        assert user_exists(username='CARLOS') is True
