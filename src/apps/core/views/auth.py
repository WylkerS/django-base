from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    erro = None
    email = ""
    proximo = request.POST.get("next") or request.GET.get("next", "")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("password", "")

        user = authenticate(request, username=email, password=senha)
        if user is not None:
            auth_login(request, user)
            return redirect(proximo or "home")
        erro = "E-mail ou senha inválidos."

    return render(request, "core/login.html", {"erro": erro, "email": email, "proximo": proximo})


@require_POST
def logout_view(request):
    auth_logout(request)
    return redirect("login")
