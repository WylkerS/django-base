from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    # Apps de domínio: path('<prefixo>/', include('apps.<nome>.urls')),
]
