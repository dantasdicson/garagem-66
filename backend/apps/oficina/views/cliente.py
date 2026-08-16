from rest_framework.viewsets import ModelViewSet
from ..models import Cliente
from ..serializers import ClienteSerializer
from apps.usuarios.models import Usuario
from apps.usuarios.permissions import PodeGerenciarOperacao, SenhaAtualizada

class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def get_permissions(self):
        return [(SenhaAtualizada if self.request.method in ("GET", "HEAD", "OPTIONS") else PodeGerenciarOperacao)()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.tipo == Usuario.Tipo.CLIENTE:
            return queryset.filter(usuario=self.request.user)
        return queryset
