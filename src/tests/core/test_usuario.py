from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from apps.core.models import Usuario


class UsuarioTests(TestCase):
    def test_modelo_de_usuario_do_projeto_e_o_usuario_do_core(self):
        self.assertIs(get_user_model(), Usuario)

    def test_email_duplicado_e_rejeitado(self):
        Usuario.objects.create_user(username="ana", email="ana@exemplo.com", password="123")

        with self.assertRaises(IntegrityError):
            Usuario.objects.create_user(username="ana2", email="ana@exemplo.com", password="123")
