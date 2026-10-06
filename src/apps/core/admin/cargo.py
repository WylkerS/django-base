from django.contrib import admin

from apps.core.models import Cargo


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ["user", "setor", "nivel", "ativo"]
    list_filter = ["nivel", "ativo", "setor"]
    search_fields = ["user__username", "user__email", "setor__nome"]
    autocomplete_fields = ["user", "setor"]
