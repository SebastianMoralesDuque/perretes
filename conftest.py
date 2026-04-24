"""
conftest.py — Fixtures globales reutilizables para toda la suite de tests.

Justificación arquitectónica:
- Las fixtures de pytest son inyectables por dependencia, eliminando
  la duplicación de setup en cada test.
- `@pytest.fixture` con `scope='function'` (default) aísla el estado
  entre tests, evitando efectos colaterales.
- `@pytest.fixture` con `scope='session'` reutiliza objetos pesados
  (ej. configuración) sin recrearlos.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.users.tests.factories import UserFactory

User = get_user_model()


# ──────────────────────────────────────────────
# Clientes HTTP
# ──────────────────────────────────────────────

@pytest.fixture
def api_client() -> APIClient:
    """Cliente DRF sin autenticación para tests de API públicos."""
    return APIClient()


@pytest.fixture
def authenticated_client(db) -> APIClient:
    """Cliente DRF autenticado con un usuario de prueba.

    Útil para tests que requieren sesión activa sin repetir login().
    El usuario autenticado se expone como `client._user` para fácil acceso.
    """
    user = UserFactory()
    client = APIClient()
    client.force_login(user)
    client._user = user
    return client


# ──────────────────────────────────────────────
# Factories comunes
# ──────────────────────────────────────────────

@pytest.fixture
def user(db):
    """Usuario estándar generado con Factory Boy."""
    return UserFactory()


@pytest.fixture
def another_user(db):
    """Segundo usuario estándar para tests de permisos cruzados."""
    return UserFactory(username='otro_user')
