"""
test_tasks.py — Tests para tareas Celery (asíncronas).

Estrategia:
- NUNCA ejecutamos tareas reales de Celery en tests unitarios.
- Usamos `CELERY_TASK_ALWAYS_EAGER = True` en settings de test
  (ya está en settings.py como DEBUG, pero pytest-django crea su propia
  configuración). En su lugar, mockeamos `.delay()` para verificar
  que el service la llama con los argumentos correctos.
- Para el cuerpo de la tarea, la testeamos aislada como una función
  pura (mock logger).

Justificación:
- Ejecutar Celery real introduce dependencia de Redis/Broker.
- Los tests deben ser deterministas y rápidos (< 50ms).
- El contrato que nos importa es: "¿Se encola la tarea?" y
  "¿Con los parámetros correctos?", no "¿El broker funciona?".
"""

import pytest

pytestmark = [pytest.mark.unit]

from unittest.mock import patch
from celery.exceptions import Retry

from apps.barkposts.tasks import log_barkpost_activity


# ═══════════════════════════════════════════════
# Verificación de encolado (vía mocks en services)
# ═══════════════════════════════════════════════

class TestTaskEnqueue:
    """
    La verificación de que la tarea se encola correctamente
    la hacemos en test_services.py (ver TestBarkPostCreate).

    Aquí testeamos el cuerpo de la tarea en aislamiento.
    """

    @patch('apps.barkposts.tasks.logger')
    def test_loguea_actividad_correctamente(self, mock_logger):
        """
        Dado user_id, username y barkpost_id,
        cuando ejecuto la tarea,
        entonces logueo un INFO con esos datos.
        """
        # Act
        # Usamos .run() para ejecutar el cuerpo de la tarea sin Celery.
        # Con bind=True, Celery inyecta self automáticamente.
        log_barkpost_activity.run(user_id=42, username='juan', barkpost_id=99)

        # Assert
        mock_logger.info.assert_called_once_with(
            '[ACTIVITY] User juan (ID: 42) created barkpost 99'
        )

    @patch.object(log_barkpost_activity, 'retry')
    @patch('apps.barkposts.tasks.logger')
    def test_reintenta_si_falla_log(self, mock_logger, mock_retry):
        """
        Dado que el logger lanza una excepción,
        cuando ejecuto la tarea,
        entonces logueo el error y reintento.
        """
        mock_logger.info.side_effect = RuntimeError('Disk full')
        mock_retry.side_effect = Retry()

        with pytest.raises(Retry):
            log_barkpost_activity.run(user_id=1, username='a', barkpost_id=1)

        mock_logger.error.assert_called_once()
        mock_retry.assert_called_once()
