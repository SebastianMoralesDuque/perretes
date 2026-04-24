"""
factories.py — Generación de datos de prueba para la app users.

Por qué Factory Boy y no fixtures manuales:
- Fixtures de Django son estáticas: cualquier cambio en el modelo
  rompe docenas de tests. Factory Boy genera datos dinámicos.
- Faker integrado permite valores realistas sin hardcodear.
- SubFactory y Trait permiten composición de escenarios complejos.
- batch_strategy='create' acelera la creación masiva en tests.
"""

import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory para usuarios con contraseña hasheada automáticamente."""

    class Meta:
        model = User
        django_get_or_create = ('username',)

    # Faker genera valores únicos por defecto; fallback para evitar colisiones
    username = factory.Sequence(lambda n: f'testuser{n}')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    avatar_choice = factory.Iterator(range(1, 9))

    class Params:
        """Traits para escenarios específicos sin crear factories nuevas."""

        inactive = factory.Trait(
            is_active=False,
        )

        staff = factory.Trait(
            is_staff=True,
        )
