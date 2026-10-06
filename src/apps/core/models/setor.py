from django.db import models

class Setor(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    ativo = models.BooleanField(default=True)
    gestor_sistema = models.BooleanField(
        default=False,
        help_text=(
            "Marca este setor como parte da equipe gestora do sistema "
            "(acesso às áreas protegidas por @gestor_requerido)."
        ),
    )

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ['nome']

    def __str__(self):
        return self.nome
