"""
test_services.py — Tests unitarios para la capa de negocio de barkposts.

Estrategia:
- Mockeamos el ORM (BarkPost.objects) para no tocar la BD.
- Mockeamos la tarea Celery (log_barkpost_activity.delay) para no
  depender de Redis ni ejecutar async.
- Testeamos la lógica de negocio: permisos, validaciones, side-effects.
"""

import pytest

pytestmark = [pytest.mark.unit]

import pytest
from unittest.mock import MagicMock, patch
from django.core.exceptions import ValidationError, PermissionDenied

from apps.barkposts.models import BarkPost
from apps.barkposts.services.bark_service import (
    barkpost_create,
    barkpost_update,
    barkpost_delete,
    barkpost_like_toggle,
)


# ═══════════════════════════════════════════════
# barkpost_create
# ═══════════════════════════════════════════════

class TestBarkPostCreate:
    """Suite para la creación de ladridos."""

    @patch('apps.barkposts.services.bark_service.log_barkpost_activity')
    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_crea_bark_con_contenido_valido(self, mock_model, mock_task):
        """
        Dado un usuario y contenido de 140 chars o menos,
        cuando llamo a barkpost_create,
        entonces creo el registro, encolo tarea async, y retorno la instancia.
        """
        mock_user = MagicMock()
        mock_user.id = 42
        mock_user.username = 'tester'
        mock_bark = MagicMock()
        mock_model.objects.create.return_value = mock_bark

        result = barkpost_create(
            user=mock_user,
            content='  Hola mundo  ',
        )

        mock_model.objects.create.assert_called_once_with(
            user=mock_user,
            content='Hola mundo',
            image=None,
        )
        mock_task.delay.assert_called_once_with(
            user_id=42,
            username='tester',
            barkpost_id=mock_bark.id,
        )
        assert result == mock_bark

    @patch('apps.barkposts.services.bark_service.log_barkpost_activity')
    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_crea_bark_con_imagen(self, mock_model, mock_task):
        """
        Dado un usuario, contenido e imagen,
        cuando llamo a barkpost_create,
        entonces la imagen se pasa al create.
        """
        mock_user = MagicMock()
        mock_image = MagicMock()
        mock_model.objects.create.return_value = MagicMock()

        barkpost_create(user=mock_user, content='Foto!', image=mock_image)

        _, kwargs = mock_model.objects.create.call_args
        assert kwargs['image'] == mock_image

    @patch('apps.barkposts.services.bark_service.log_barkpost_activity')
    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_tolerancia_falla_celery_no_rompe_flujo(self, mock_model, mock_task):
        """
        Dado que la tarea Celery falla al encolar (ej. Redis caído),
        cuando llamo a barkpost_create,
        entonces el ladrido se crea igual y se loguea el warning.
        """
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'u'
        mock_model.objects.create.return_value = MagicMock()
        mock_task.delay.side_effect = Exception('Redis down')

        result = barkpost_create(user=mock_user, content='x')

        assert result is not None  # No explota
        mock_task.delay.assert_called_once()


# ═══════════════════════════════════════════════
# barkpost_update
# ═══════════════════════════════════════════════

class TestBarkPostUpdate:
    """Suite para la edición de ladridos."""

    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_actualiza_contenido_si_es_dueño(self, mock_model):
        """
        Dado un ladrido propio,
        cuando actualizo el contenido,
        entonces se guarda el nuevo texto.
        """
        mock_user = MagicMock()
        mock_user.id = 7
        mock_bark = MagicMock()
        mock_bark.user_id = 7
        mock_bark.image = None
        mock_model.objects.select_related.return_value.get.return_value = mock_bark

        result = barkpost_update(
            user=mock_user,
            barkpost_id=1,
            content='Nuevo texto',
        )

        assert mock_bark.content == 'Nuevo texto'
        mock_bark.save.assert_called_once()
        assert result == mock_bark

    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_rechaza_edicion_si_no_es_dueño(self, mock_model):
        """
        Dado un ladrido de otro usuario,
        cuando intento editarlo,
        entonces lanza PermissionDenied.
        """
        mock_user = MagicMock()
        mock_user.id = 7
        mock_bark = MagicMock()
        mock_bark.user_id = 99  # Otro usuario
        mock_model.objects.select_related.return_value.get.return_value = mock_bark

        with pytest.raises(PermissionDenied, match='no es tuyo'):
            barkpost_update(user=mock_user, barkpost_id=1, content='Hackeo')

        mock_bark.save.assert_not_called()

    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_lanza_error_si_bark_no_existe(self, mock_model):
        """
        Dado un ID de ladrido inexistente,
        cuando intento editar,
        entonces lanza ValidationError.
        """
        # El service captura BarkPost.DoesNotExist, pero como hemos
        # parchado BarkPost con un MagicMock, DoesNotExist no es una
        # excepción válida. Creamos una excepción dummy y la asignamos.
        mock_model.DoesNotExist = type('DoesNotExist', (Exception,), {})
        mock_model.objects.select_related.return_value.get.side_effect = (
            mock_model.DoesNotExist
        )

        with pytest.raises(ValidationError, match='no existe'):
            barkpost_update(
                user=MagicMock(id=1),
                barkpost_id=9999,
                content='Nada',
            )

    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_elimina_imagen_cuando_remove_image_true(self, mock_model):
        """
        Dado un ladrido con imagen y remove_image=True,
        cuando actualizo,
        entonces borro el archivo de disco y seteo image=None.
        """
        mock_user = MagicMock()
        mock_user.id = 7
        mock_bark = MagicMock()
        mock_bark.user_id = 7
        old_image = MagicMock()
        mock_bark.image = old_image  # Tiene imagen
        mock_model.objects.select_related.return_value.get.return_value = mock_bark

        barkpost_update(
            user=mock_user,
            barkpost_id=1,
            content='Sin foto',
            remove_image=True,
        )

        old_image.delete.assert_called_once_with(save=False)
        assert mock_bark.image is None

    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_reemplaza_imagen_cuando_se_envia_nueva(self, mock_model):
        """
        Dado un ladrido con imagen existente,
        cuando subo una imagen nueva,
        entonces borro la anterior y asigno la nueva.
        """
        mock_user = MagicMock()
        mock_user.id = 7
        mock_bark = MagicMock()
        mock_bark.user_id = 7
        old_image = MagicMock()
        mock_bark.image = old_image
        new_image = MagicMock()
        mock_model.objects.select_related.return_value.get.return_value = mock_bark

        barkpost_update(
            user=mock_user,
            barkpost_id=1,
            image=new_image,
        )

        old_image.delete.assert_called_once_with(save=False)
        assert mock_bark.image == new_image


# ═══════════════════════════════════════════════
# barkpost_delete
# ═══════════════════════════════════════════════

class TestBarkPostDelete:
    """Suite para la eliminación de ladridos."""

    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_elimina_bark_si_es_dueño(self, mock_model):
        """
        Dado un ladrido propio,
        cuando llamo a barkpost_delete,
        entonces se borra el registro y la imagen del disco.
        """
        mock_user = MagicMock()
        mock_user.id = 7
        mock_bark = MagicMock()
        mock_bark.user_id = 7
        mock_bark.image = MagicMock()
        mock_model.objects.select_related.return_value.get.return_value = mock_bark

        barkpost_delete(user=mock_user, barkpost_id=1)

        mock_bark.image.delete.assert_called_once_with(save=False)
        mock_bark.delete.assert_called_once()

    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_rechaza_eliminacion_si_no_es_dueño(self, mock_model):
        """
        Dado un ladrido ajeno,
        cuando intento borrarlo,
        entonces lanza PermissionDenied.
        """
        mock_user = MagicMock()
        mock_user.id = 7
        mock_bark = MagicMock()
        mock_bark.user_id = 99
        mock_model.objects.select_related.return_value.get.return_value = mock_bark

        with pytest.raises(PermissionDenied):
            barkpost_delete(user=mock_user, barkpost_id=1)

        mock_bark.delete.assert_not_called()


# ═══════════════════════════════════════════════
# barkpost_like_toggle
# ═══════════════════════════════════════════════

class TestBarkPostLikeToggle:
    """Suite para el toggle de likes."""

    @patch('apps.barkposts.services.bark_service.Like')
    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_da_like_cuando_no_existe(self, mock_post_model, mock_like_model):
        """
        Dado un ladrido sin like previo del usuario,
        cuando llamo a like_toggle,
        entonces creo like y retorno is_liked=True.
        """
        mock_user = MagicMock()
        mock_bark = MagicMock()
        mock_post_model.objects.get.return_value = mock_bark

        mock_like = MagicMock()
        mock_like_model.objects.get_or_create.return_value = (mock_like, True)
        mock_like_model.objects.filter.return_value.count.return_value = 1

        result = barkpost_like_toggle(user=mock_user, barkpost_id=1)

        assert result['is_liked'] is True
        assert result['likes_count'] == 1

    @patch('apps.barkposts.services.bark_service.Like')
    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_quita_like_cuando_ya_existe(self, mock_post_model, mock_like_model):
        """
        Dado un ladrido con like previo del usuario,
        cuando llamo a like_toggle,
        entonces borro el like y retorno is_liked=False.
        """
        mock_user = MagicMock()
        mock_bark = MagicMock()
        mock_post_model.objects.get.return_value = mock_bark

        mock_like = MagicMock()
        mock_like_model.objects.get_or_create.return_value = (mock_like, False)
        mock_like_model.objects.filter.return_value.count.return_value = 0

        result = barkpost_like_toggle(user=mock_user, barkpost_id=1)

        mock_like.delete.assert_called_once()
        assert result['is_liked'] is False
        assert result['likes_count'] == 0

    @patch('apps.barkposts.services.bark_service.BarkPost')
    def test_lanza_error_si_bark_no_existe(self, mock_model):
        """
        Dado un ID de ladrido inexistente,
        cuando llamo a like_toggle,
        entonces lanza ValidationError.
        """
        mock_model.DoesNotExist = type('DoesNotExist', (Exception,), {})
        mock_model.objects.get.side_effect = mock_model.DoesNotExist

        with pytest.raises(ValidationError, match='no existe'):
            barkpost_like_toggle(user=MagicMock(), barkpost_id=9999)
