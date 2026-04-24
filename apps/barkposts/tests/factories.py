"""
factories.py — Generación de datos de prueba para la app barkposts.
"""

import factory
from apps.barkposts.models import BarkPost, Like
from apps.users.tests.factories import UserFactory


class BarkPostFactory(factory.django.DjangoModelFactory):
    """Factory para ladridos (BarkPost) con contenido variado."""

    class Meta:
        model = BarkPost

    user = factory.SubFactory(UserFactory)
    content = factory.Faker('sentence', nb_words=10)

    class Params:
        """Traits para escenarios específicos."""

        empty_content = factory.Trait(
            content='',
        )

        long_content = factory.Trait(
            # 141 caracteres para forzar el límite de 140
            content='x' * 141,
        )

        max_content = factory.Trait(
            # Exactamente 140 caracteres (límite válido)
            content='x' * 140,
        )


class LikeFactory(factory.django.DjangoModelFactory):
    """Factory para likes entre usuarios y ladridos."""

    class Meta:
        model = Like

    user = factory.SubFactory(UserFactory)
    barkpost = factory.SubFactory(BarkPostFactory)
