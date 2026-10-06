from apps.core.models import Cargo


def usuario_e_gestor(user):
    """True se `user` faz parte da equipe gestora do sistema."""
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return Cargo.objects.filter(
        user=user,
        ativo=True,
        setor__ativo=True,
        setor__gestor_sistema=True,
    ).exists()
