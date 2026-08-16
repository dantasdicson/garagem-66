from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AlterarSenhaView, PerfilAtualView, UsuarioViewSet

router = DefaultRouter()
router.register("", UsuarioViewSet, basename="usuario")

urlpatterns = [
    path("me/", PerfilAtualView.as_view(), name="perfil-atual"),
    path("alterar-senha/", AlterarSenhaView.as_view(), name="alterar-senha"),
] + router.urls
