from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def log_barkpost_activity(self, user_id: int, username: str, barkpost_id: int):
    """
    Tarea asíncrona para registrar la actividad de creación de un ladrido.
    
    JUSTIFICACIÓN TÉCNICA:
    - Esta tarea se ejecuta fuera del ciclo request/response.
    - El logging y las métricas son operaciones de I/O que no deben bloquear
      el thread de respuesta HTTP.
    - Si en el futuro queremos enviar notificaciones push, emails o métricas
      a un sistema externo (DataDog, Prometheus), Celery desacopla esa
      responsabilidad sin afectar la latencia del endpoint.
    - En producción, podríamos reemplazar este logger por un event stream
      (Kafka, RabbitMQ) sin tocar la lógica de negocio.
    
    Args:
        user_id: ID del usuario que creó el ladrido.
        username: Username del usuario.
        barkpost_id: ID del ladrido creado.
    """
    try:
        logger.info(
            f'[ACTIVITY] User {username} (ID: {user_id}) created barkpost {barkpost_id}'
        )
        # Aquí podríamos:
        # - Incrementar un contador en Redis
        # - Enviar un email de notificación
        # - Publicar en un canal de WebSocket
        # - Enviar métricas a Prometheus
    except Exception as exc:
        # Si falla, reintenta con backoff exponencial
        logger.error(f'Error logging activity: {exc}')
        raise self.retry(exc=exc, countdown=60)
