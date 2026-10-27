from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LoginViewTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username="ana@exemplo.com", email="ana@exemplo.com", password="senha-forte-123"
        )

    def test_pagina_de_login_retorna_200(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/login.html")

    def test_credenciais_validas_autenticam_e_redirecionam_para_home(self):
        response = self.client.post(
            reverse("login"), {"email": "ana@exemplo.com", "password": "senha-forte-123"}
        )
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.usuario.pk)

    def test_credenciais_validas_respeitam_next(self):
        response = self.client.post(
            reverse("login"),
            {"email": "ana@exemplo.com", "password": "senha-forte-123", "next": "/admin/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/")

    def test_credenciais_invalidas_mostram_erro(self):
        response = self.client.post(
            reverse("login"), {"email": "ana@exemplo.com", "password": "errada"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "E-mail ou senha inválidos.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_usuario_autenticado_e_redirecionado_para_home(self):
        self.client.force_login(self.usuario)
        response = self.client.get(reverse("login"))
        self.assertRedirects(response, reverse("home"))

    def test_logout_exige_post(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)
