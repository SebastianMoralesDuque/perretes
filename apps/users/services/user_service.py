from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError

User = get_user_model()


def user_create(*, username: str, password: str, avatar_choice: int = 1) -> User:
    """
    Crea un nuevo usuario con contraseña hasheada.

    Args:
        username: Nombre de usuario único.
        password: Contraseña en texto plano.
        avatar_choice: Avatar predeterminado (1-8).

    Returns:
        Instancia de User creada.

    Raises:
        ValidationError: Si el usuario ya existe o la contraseña no es válida.
    """
    if User.objects.filter(username__iexact=username).exists():
        raise ValidationError('Este nombre de usuario ya está registrado.')

    user = User.objects.create_user(
        username=username.lower().strip(),
        password=password,
        avatar_choice=avatar_choice
    )
    return user


def user_authenticate_and_login(*, request, username: str, password: str):
    """
    Autentica un usuario y crea su sesión.
    
    Args:
        request: HttpRequest actual.
        username: Nombre de usuario.
        password: Contraseña en texto plano.
        
    Returns:
        Instancia de User autenticado.
        
    Raises:
        ValidationError: Si las credenciales son incorrectas.
    """
    user = authenticate(
        request=request,
        username=username.lower().strip(),
        password=password
    )
    
    if user is None:
        raise ValidationError('Nombre de usuario o contraseña incorrectos.')
    
    if not user.is_active:
        raise ValidationError('Esta cuenta está desactivada.')
    
    login(request, user)
    return user
