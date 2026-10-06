from django.conf import settings

from apps.core.selectors.permissoes import usuario_e_gestor

# Namespace de URL -> seção da navegação. Cada app de domínio registra aqui a sua
# (ex. "pedidos": "pedidos"); rotas sem namespace caem em SECOES_POR_ROTA.
SECOES_POR_NAMESPACE = {}
SECOES_POR_ROTA = {"home": "inicio"}


def contexto_app(request):
    return {"app_nome": settings.APP_NOME}


def contexto_permissoes(request):
    usuario = getattr(request, "user", None)
    eh_gestor = bool(usuario and usuario.is_authenticated and usuario_e_gestor(usuario))
    return {"usuario_e_gestor": eh_gestor}


def _secao_da_rota(rota):
    if rota is None:
        return ""
    if rota.namespace:
        return SECOES_POR_NAMESPACE.get(rota.namespace, "")
    return SECOES_POR_ROTA.get(rota.url_name, "")


def contexto_navegacao(request):
    """`secao_ativa` destaca o item certo da navegação no `base.html`."""
    return {"secao_ativa": _secao_da_rota(getattr(request, "resolver_match", None))}
