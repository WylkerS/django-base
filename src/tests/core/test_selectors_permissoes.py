from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from apps.core.models import Cargo, Setor
from apps.core.selectors.permissoes import usuario_e_gestor

User = get_user_model()


class UsuarioEGestorTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="comum", password="123")
        self.setor = Setor.objects.create(nome="TI", gestor_sistema=True)

    def test_usuario_anonimo_nao_e_gestor(self):
        self.assertFalse(usuario_e_gestor(AnonymousUser()))

    def test_superusuario_e_sempre_gestor(self):
        superusuario = User.objects.create_superuser(
            username="admin", password="123", email="admin@exemplo.com"
        )
        self.assertTrue(usuario_e_gestor(superusuario))

    def test_superusuario_e_gestor_mesmo_sem_setor_gestor(self):
        superusuario = User.objects.create_superuser(
            username="admin2", password="123", email="admin2@exemplo.com"
        )
        Setor.objects.all().update(gestor_sistema=False)
        self.assertTrue(usuario_e_gestor(superusuario))

    def test_usuario_com_cargo_ativo_em_setor_gestor_e_gestor(self):
        Cargo.objects.create(
            user=self.usuario, setor=self.setor, nivel="analista", ativo=True
        )
        self.assertTrue(usuario_e_gestor(self.usuario))

    def test_usuario_sem_cargo_nao_e_gestor(self):
        self.assertFalse(usuario_e_gestor(self.usuario))

    def test_cargo_inativo_nao_concede_gestao(self):
        Cargo.objects.create(
            user=self.usuario, setor=self.setor, nivel="analista", ativo=False
        )
        self.assertFalse(usuario_e_gestor(self.usuario))

    def test_setor_inativo_nao_concede_gestao(self):
        self.setor.ativo = False
        self.setor.save()
        Cargo.objects.create(
            user=self.usuario, setor=self.setor, nivel="analista", ativo=True
        )
        self.assertFalse(usuario_e_gestor(self.usuario))

    def test_setor_nao_gestor_nao_concede_gestao(self):
        setor_comum = Setor.objects.create(nome="Financeiro", gestor_sistema=False)
        Cargo.objects.create(
            user=self.usuario, setor=setor_comum, nivel="analista", ativo=True
        )
        self.assertFalse(usuario_e_gestor(self.usuario))
