"""
test_selectors.py — Tests para los selectores (queries) de barkposts.

Nota:
- Estos tests SÍ tocan la base de datos porque testean el ORM real.
- Usamos `@pytest.mark.django_db` para que pytest-django maneje
  la transacción y el rollback automático entre tests.
"""

import pytest

pytestmark = [pytest.mark.integration]
from datetime import timedelta
from django.utils import timezone

from apps.barkposts.selectors.bark_selector import (
    barkpost_list_all,
    barkpost_list_by_user,
    barkpost_get_by_id,
    barkpost_is_liked_by_user,
)
from apps.barkposts.tests.factories import BarkPostFactory, LikeFactory
from apps.users.tests.factories import UserFactory


# ═══════════════════════════════════════════════
# barkpost_list_all
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostListAll:
    """Suite para el feed global de ladridos."""

    def test_retorna_todos_los_barks_ordenados_desc(self):
        """
        Dado 3 ladridos creados en distintos momentos,
        cuando listo todos,
        entonces están ordenados del más reciente al más antiguo.
        """
        user = UserFactory()
        old = BarkPostFactory(user=user)
        old.created_at = timezone.now() - timedelta(hours=2)
        old.save()

        mid = BarkPostFactory(user=user)
        mid.created_at = timezone.now() - timedelta(hours=1)
        mid.save()

        new = BarkPostFactory(user=user)

        result = list(barkpost_list_all(user=None))

        ids = [b.id for b in result]
        assert ids == [new.id, mid.id, old.id]

    def test_anonimo_no_tiene_is_liked_by_me(self):
        """
        Dado un visitante anónimo,
        cuando listo barks,
        entonces is_liked_by_me es False para todos.
        """
        BarkPostFactory()

        result = list(barkpost_list_all(user=None))

        assert result[0].is_liked_by_me is False

    def test_autenticado_ve_sus_likes(self):
        """
        Dado un usuario que dio like a un ladrido,
        cuando listo como ese usuario,
        entonces is_liked_by_me es True solo para ese bark.
        """
        user = UserFactory()
        liked_bark = BarkPostFactory()
        unliked_bark = BarkPostFactory()
        LikeFactory(user=user, barkpost=liked_bark)

        result = list(barkpost_list_all(user=user))

        liked = next(b for b in result if b.id == liked_bark.id)
        unliked = next(b for b in result if b.id == unliked_bark.id)

        assert liked.is_liked_by_me is True
        assert unliked.is_liked_by_me is False

    def test_incluye_likes_count(self):
        """
        Dado un ladrido con 3 likes,
        cuando listo,
        entonces likes_count == 3.
        """
        bark = BarkPostFactory()
        LikeFactory.create_batch(3, barkpost=bark)

        result = list(barkpost_list_all(user=None))

        assert result[0].likes_count == 3


# ═══════════════════════════════════════════════
# barkpost_list_by_user
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostListByUser:
    """Suite para el perfil de un usuario específico."""

    def test_retorna_solo_barks_del_usuario_solicitado(self):
        """
        Dado usuario A con 2 barks y usuario B con 1 bark,
        cuando listo por usuario A,
        entonces retorno solo los 2 de A.
        """
        user_a = UserFactory()
        user_b = UserFactory()
        BarkPostFactory.create_batch(2, user=user_a)
        BarkPostFactory(user=user_b)

        result = list(barkpost_list_by_user(user_id=user_a.id, viewer=None))

        assert len(result) == 2
        assert all(b.user_id == user_a.id for b in result)

    def test_orden_descendente_por_fecha(self):
        """
        Dado un usuario con 2 barks en distintas fechas,
        cuando listo por ese usuario,
        entonces el más reciente aparece primero.
        """
        user = UserFactory()
        old = BarkPostFactory(user=user)
        old.created_at = timezone.now() - timedelta(days=1)
        old.save()

        new = BarkPostFactory(user=user)

        result = list(barkpost_list_by_user(user_id=user.id, viewer=None))

        assert result[0].id == new.id
        assert result[1].id == old.id


# ═══════════════════════════════════════════════
# barkpost_get_by_id
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostGetById:
    """Suite para obtención de un ladrido por ID."""

    def test_retorna_bark_existente(self):
        """
        Dado un ladrido con ID conocido,
        cuando lo busco por ID,
        entonces retorno la instancia correcta.
        """
        bark = BarkPostFactory()

        result = barkpost_get_by_id(barkpost_id=bark.id, viewer=None)

        assert result == bark

    def test_retorna_none_si_no_existe(self):
        """
        Dado un ID inexistente,
        cuando lo busco,
        entonces retorno None.
        """
        result = barkpost_get_by_id(barkpost_id=99999, viewer=None)

        assert result is None

    def test_anota_likes_correctamente(self):
        """
        Dado un ladrido con 2 likes,
        cuando lo busco por ID,
        entonces likes_count == 2.
        """
        bark = BarkPostFactory()
        LikeFactory.create_batch(2, barkpost=bark)

        result = barkpost_get_by_id(barkpost_id=bark.id, viewer=None)

        assert result.likes_count == 2


# ═══════════════════════════════════════════════
# barkpost_is_liked_by_user
# ═══════════════════════════════════════════════

@pytest.mark.django_db
class TestBarkPostIsLikedByUser:
    """Suite para verificación de like."""

    def test_retorna_true_si_usuario_dio_like(self):
        """
        Dado un like existente,
        cuando pregunto si el usuario dio like,
        entonces retorno True.
        """
        user = UserFactory()
        bark = BarkPostFactory()
        LikeFactory(user=user, barkpost=bark)

        assert barkpost_is_liked_by_user(user_id=user.id, barkpost_id=bark.id) is True

    def test_retorna_false_si_no_dio_like(self):
        """
        Dado que no existe like,
        cuando pregunto,
        entonces retorno False.
        """
        user = UserFactory()
        bark = BarkPostFactory()

        assert barkpost_is_liked_by_user(user_id=user.id, barkpost_id=bark.id) is False
