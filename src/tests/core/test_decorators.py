from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from apps.core.decorators import gestor_requerido
from apps.core.models import Cargo, Setor

User = get_user_model()


@gestor_requerido
def view_protegida(request):
    return HttpResponse("ok")


class GestorRequeridoTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.setor = Setor.objects.create(nome="TI", gestor_sistema=True)

    def _request_autenticado(self, usuario):
        request = self.factory.get("/protegida/")
        request.user = usuario
        return request

    def test_usuario_anonimo_e_redirecionado_para_login(self):
        from django.contrib.auth.models import AnonymousUser

        request = self._request_autenticado(AnonymousUser())
        response = view_protegida(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        self.assertIn("next=", response.url)

    def test_usuario_autenticado_sem_gestao_recebe_permission_denied(self):
        usuario = User.objects.create_user(username="comum", password="123")
        request = self._request_autenticado(usuario)
        with self.assertRaises(PermissionDenied):
            view_protegida(request)

    def test_usuario_gestor_executa_a_view(self):
        usuario = User.objects.create_user(username="gestor", password="123")
        Cargo.objects.create(
            user=usuario, setor=self.setor, nivel="analista", ativo=True
        )
        request = self._request_autenticado(usuario)
        response = view_protegida(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")
