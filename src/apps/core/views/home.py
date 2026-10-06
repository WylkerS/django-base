from django.shortcuts import render


def home_view(request):
    """Página inicial pública. Cada projeto substitui o conteúdo por seu painel/atalhos."""
    return render(request, "core/home.html")
