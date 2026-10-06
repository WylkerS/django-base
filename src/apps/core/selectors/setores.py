from apps.core.models import Cargo, Setor


def listar_setores_ativos():
    return Setor.objects.filter(ativo=True).order_by("nome")


def obter_setor_principal(usuario):
    """Setor do primeiro cargo ativo (em setor ativo) do usuário, ou None."""
    cargo = (
        Cargo.objects.filter(user=usuario, ativo=True, setor__ativo=True)
        .select_related("setor")
        .order_by("setor__nome")
        .first()
    )
    return cargo.setor if cargo else None
