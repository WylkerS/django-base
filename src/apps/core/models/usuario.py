from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuário autenticável do sistema, extensível pelo app core."""

    email = models.EmailField(
        "email address",
        max_length=254,
        unique=True,
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
