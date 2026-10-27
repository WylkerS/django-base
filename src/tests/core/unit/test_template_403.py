from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, SimpleTestCase
from django.views.defaults import permission_denied


class Template403Tests(SimpleTestCase):
    def test_acesso_negado_usa_o_template_do_projeto(self):
        request = RequestFactory().get("/area-da-gestao/")
        request.user = AnonymousUser()

        response = permission_denied(request, PermissionDenied())

        self.assertEqual(response.status_code, 403)
        self.assertIn("Acesso não autorizado", response.content.decode())
        self.assertIn("Voltar ao início", response.content.decode())
