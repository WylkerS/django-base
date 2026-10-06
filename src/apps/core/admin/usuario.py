from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.core.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Administração do usuário customizado com os formulários do Django."""
