from django.contrib import admin

from apps.core.models import Cargo, Setor


class CargoInline(admin.TabularInline):
    model = Cargo
    extra = 0
    autocomplete_fields = ["user"]


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ["nome", "gestor_sistema", "ativo"]
    list_filter = ["gestor_sistema", "ativo"]
    search_fields = ["nome"]
    inlines = [CargoInline]
