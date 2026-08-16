from rest_framework.viewsets import ModelViewSet
from ..models import ItemServico
from ..serializers import ItemServicoSerializer
from apps.usuarios.permissions import IsEquipeOficina, PodeGerenciarOperacao
from apps.usuarios.models import Usuario

class ItemServicoViewSet(ModelViewSet):
    queryset = ItemServico.objects.select_related("ordem_servico").all()
    serializer_class = ItemServicoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.tipo == Usuario.Tipo.MECANICO:
            return queryset.filter(ordem_servico__mecanico=self.request.user)
        return queryset

    def get_permissions(self):
        return [IsEquipeOficina()]
