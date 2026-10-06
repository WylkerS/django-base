from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from apps.core.selectors.permissoes import usuario_e_gestor


def gestor_requerido(view_func):
    """Protege uma view exigindo autenticação + papel de gestor do sistema."""

    @wraps(view_func)
    def view_envolvida(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not usuario_e_gestor(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return view_envolvida
