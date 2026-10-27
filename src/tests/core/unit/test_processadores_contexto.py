from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase, override_settings

from apps.core.processadores_contexto import (
    SECOES_POR_NAMESPACE,
    contexto_app,
    contexto_navegacao,
    contexto_permissoes,
)


class ContextoAppTests(SimpleTestCase):
    @override_settings(APP_NOME="Sistema de Teste")
    def test_retorna_o_nome_configurado(self):
        self.assertEqual(contexto_app(None), {"app_nome": "Sistema de Teste"})


class ContextoPermissoesTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_usuario_anonimo_nao_e_gestor(self):
        request = self.rf.get("/")
        request.user = AnonymousUser()

        self.assertEqual(contexto_permissoes(request), {"usuario_e_gestor": False})

    def test_request_sem_usuario_nao_e_gestor(self):
        self.assertEqual(contexto_permissoes(self.rf.get("/")), {"usuario_e_gestor": False})

    def test_superusuario_e_gestor_sem_consultar_o_banco(self):
        request = self.rf.get("/")
        request.user = SimpleNamespace(is_authenticated=True, is_superuser=True)

        self.assertEqual(contexto_permissoes(request), {"usuario_e_gestor": True})


class ContextoNavegacaoTests(SimpleTestCase):
    def _request(self, *, namespace="", url_name=None):
        request = RequestFactory().get("/")
        request.resolver_match = SimpleNamespace(namespace=namespace, url_name=url_name)
        return request

    def test_sem_rota_resolvida_nao_ha_secao_ativa(self):
        self.assertEqual(contexto_navegacao(RequestFactory().get("/")), {"secao_ativa": ""})

    def test_rota_sem_namespace_usa_secoes_por_rota(self):
        self.assertEqual(
            contexto_navegacao(self._request(url_name="home")), {"secao_ativa": "inicio"}
        )

    def test_rota_com_namespace_usa_secoes_por_namespace(self):
        with patch.dict(SECOES_POR_NAMESPACE, {"pedidos": "pedidos"}):
            contexto = contexto_navegacao(self._request(namespace="pedidos", url_name="painel"))

        self.assertEqual(contexto, {"secao_ativa": "pedidos"})

    def test_namespace_nao_registrado_nao_ha_secao_ativa(self):
        contexto = contexto_navegacao(self._request(namespace="desconhecido", url_name="x"))

        self.assertEqual(contexto, {"secao_ativa": ""})

