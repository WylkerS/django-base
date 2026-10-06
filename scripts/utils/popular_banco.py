"""Popula o banco de desenvolvimento com um cenário mínimo: um setor gestor, um setor
comum e dois usuários de exemplo (sem senha utilizável). Idempotente — registros
existentes (por nome/username) não são alterados. Recusa rodar com DEBUG desligado.

Cada projeto acrescenta aqui os dados do seu domínio, seguindo o mesmo padrão
(`get_or_create` + contagem no resumo).

Uso (no host; o script roda dentro de django-web):
    docker compose -f docker-compose.dev.yml exec django-web python /app/scripts/utils/popular_banco.py
"""
import os
import sys
from collections import defaultdict

import django
from dotenv import load_dotenv


# SETUP DJANGO
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, "src"))

load_dotenv(os.path.join(BASE_DIR, ".env"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


from django.conf import settings  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from django.db import transaction  # noqa: E402

from apps.core.models import Cargo, Setor  # noqa: E402


# DADOS
SETORES = [
    # nome (minúsculo, canônico), gestor do sistema
    ("administrativo", True),
    ("operacional", False),
]

USUARIOS = [
    # e-mail (também é o username), nome, sobrenome, setor, nível
    ("gestor@exemplo.com", "Gestor", "Exemplo", "administrativo", "analista"),
    ("usuario@exemplo.com", "Usuário", "Exemplo", "operacional", "analista"),
]


def popular_setores_e_usuarios(resumo):
    for nome, gestor_sistema in SETORES:
        _, criado = Setor.objects.get_or_create(nome=nome, defaults={"gestor_sistema": gestor_sistema})
        resumo["setores"][criado] += 1

    Usuario = get_user_model()
    for email, nome, sobrenome, nome_setor, nivel in USUARIOS:
        usuario, criado = Usuario.objects.get_or_create(
            username=email,
            defaults={"email": email, "first_name": nome, "last_name": sobrenome},
        )
        if criado:
            usuario.set_unusable_password()
            usuario.save(update_fields=["password"])
        resumo["usuarios"][criado] += 1
        Cargo.objects.get_or_create(
            user=usuario,
            setor=Setor.objects.get(nome=nome_setor),
            ativo=True,
            defaults={"nivel": nivel},
        )


def main():
    if not settings.DEBUG:
        sys.exit("Recusado: este script só roda com DEBUG=True (banco de desenvolvimento).")

    resumo = defaultdict(lambda: {True: 0, False: 0})
    with transaction.atomic():
        popular_setores_e_usuarios(resumo)

    for entidade, contagem in resumo.items():
        print(f"{entidade}: {contagem[True]} criado(s), {contagem[False]} já existente(s)")


if __name__ == "__main__":
    main()
