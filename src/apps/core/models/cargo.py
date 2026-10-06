from django.db import models
from django.conf import settings

class Cargo(models.Model):
    NIVEL_CHOICES = [
        ('analista', 'Analista'),
        ('gerente', 'Gerente'),
        ('direcao', 'Direção'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    setor = models.ForeignKey('core.Setor', on_delete=models.CASCADE)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'setor'],
                condition=models.Q(ativo=True),
                name='unique_cargo_ativo_por_setor'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.setor.nome} ({self.nivel})"