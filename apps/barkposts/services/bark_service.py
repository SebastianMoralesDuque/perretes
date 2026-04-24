import logging
from django.core.exceptions import PermissionDenied, ValidationError
from apps.barkposts.models import BarkPost, Like
from apps.barkposts.tasks import log_barkpost_activity

logger = logging.getLogger(__name__)


def barkpost_create(*, user, content: str, image=None) -> BarkPost:
    """
    Crea un nuevo ladrido asociado a un usuario.
    """
    bark = BarkPost.objects.create(
        user=user,
        content=content.strip(),
        image=image
    )
    
    try:
        log_barkpost_activity.delay(
            user_id=user.id,
            username=user.username,
            barkpost_id=bark.id
        )
    except Exception as exc:
        logger.warning(f'No se pudo encolar tarea de logging: {exc}')
    
    return bark


def barkpost_update(*, user, barkpost_id: int, content: str = None, image=None, remove_image: bool = False) -> BarkPost:
    """
    Actualiza un ladrido existente. Solo el dueño puede editarlo.
    """
    try:
        bark = BarkPost.objects.select_related('user').get(id=barkpost_id)
    except BarkPost.DoesNotExist:
        raise ValidationError('El ladrido no existe.')
    
    if bark.user_id != user.id:
        raise PermissionDenied('No puedes editar un ladrido que no es tuyo.')
    
    if content is not None:
        bark.content = content.strip()
    
    if remove_image:
        if bark.image:
            bark.image.delete(save=False)
        bark.image = None
    elif image is not None:
        if bark.image:
            bark.image.delete(save=False)
        bark.image = image
    
    bark.save()
    return bark


def barkpost_delete(*, user, barkpost_id: int):
    """
    Elimina un ladrido existente. Solo el dueño puede eliminarlo.
    """
    try:
        bark = BarkPost.objects.select_related('user').get(id=barkpost_id)
    except BarkPost.DoesNotExist:
        raise ValidationError('El ladrido no existe.')

    if bark.user_id != user.id:
        raise PermissionDenied('No puedes eliminar un ladrido que no es tuyo.')

    if bark.image:
        bark.image.delete(save=False)
    bark.delete()


def barkpost_like_toggle(*, user, barkpost_id: int) -> dict:
    """
    Da o quita like a un ladrido.
    Retorna {'likes_count': int, 'is_liked': bool}
    """
    try:
        bark = BarkPost.objects.get(id=barkpost_id)
    except BarkPost.DoesNotExist:
        raise ValidationError('El ladrido no existe.')
    
    like, created = Like.objects.get_or_create(user=user, barkpost=bark)
    
    if not created:
        like.delete()
        is_liked = False
    else:
        is_liked = True
    
    likes_count = Like.objects.filter(barkpost=bark).count()
    
    return {
        'likes_count': likes_count,
        'is_liked': is_liked,
    }
