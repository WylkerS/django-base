from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.core.models import Cargo, Setor

User = get_user_model()


class HomeViewTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username="ana", email="ana@exemplo.com", password="123", first_name="Ana"
        )

    def test_pagina_publica_retorna_200_sem_autenticacao(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["secao_ativa"], "inicio")

    def test_usuario_anonimo_ve_botao_entrar(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Entrar")
        self.assertNotContains(response, "Sair")

    def test_usuario_autenticado_ve_nome_e_botao_sair(self):
        self.client.force_login(self.usuario)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Ana")
        self.assertContains(response, "Sair")

    def test_link_da_administracao_so_aparece_para_gestor(self):
        self.client.force_login(self.usuario)
        response = self.client.get(reverse("home"))
        self.assertFalse(response.context["usuario_e_gestor"])
        self.assertNotContains(response, reverse("admin:index"))

        setor = Setor.objects.create(nome="gestão", gestor_sistema=True)
        Cargo.objects.create(user=self.usuario, setor=setor, nivel="analista", ativo=True)
        response = self.client.get(reverse("home"))
        self.assertTrue(response.context["usuario_e_gestor"])
        self.assertContains(response, reverse("admin:index"))
