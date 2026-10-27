"""Setup compartilhado pelos testes de integração de todos os apps.

Não começa com `test_`, então não é coletado pelo test runner — só serve de
apoio para os módulos `test_*.py` de cada app.
"""
from django.contrib.auth import get_user_model
from django.test import Client

from apps.core.models import Cargo, Setor

User = get_user_model()


def login(user):
    client = Client()
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    return client


def criar_usuario_com_setor(nome_setor, username="analista", *, gestor_sistema=False):
    setor, _ = Setor.objects.get_or_create(
        nome=nome_setor, defaults={"gestor_sistema": gestor_sistema}
    )
    usuario = User.objects.create_user(username, email=f"{username}@exemplo.com", password="x")
    Cargo.objects.create(user=usuario, setor=setor, nivel="analista")
    return usuario


def criar_gestor(username="gestor", nome_setor="Gestão"):
    return criar_usuario_com_setor(nome_setor, username, gestor_sistema=True)


def criar_usuario_sem_cargo(username="semcargo"):
    return User.objects.create_user(username, email=f"{username}@exemplo.com", password="x")
