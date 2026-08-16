from rest_framework.viewsets import ModelViewSet
from ..models import Motocicleta
from ..serializers import MotocicletaSerializer
from apps.usuarios.models import Usuario
from apps.usuarios.permissions import PodeGerenciarOperacao, SenhaAtualizada

class MotocicletaViewSet(ModelViewSet):
    queryset = Motocicleta.objects.select_related("cliente").all()
    serializer_class = MotocicletaSerializer

    def get_permissions(self):
        return [(SenhaAtualizada if self.request.method in ("GET", "HEAD", "OPTIONS") else PodeGerenciarOperacao)()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.tipo == Usuario.Tipo.CLIENTE:
            return queryset.filter(cliente__usuario=self.request.user)
        return queryset
