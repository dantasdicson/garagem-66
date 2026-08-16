from rest_framework.viewsets import ModelViewSet
from ..models import ItemPeca
from ..serializers import ItemPecaSerializer
from ..services import excluir_item_peca
from apps.usuarios.permissions import IsEquipeOficina, PodeGerenciarOperacao
from apps.usuarios.models import Usuario

class ItemPecaViewSet(ModelViewSet):
    queryset = ItemPeca.objects.select_related("ordem_servico", "requisicao_peca", "peca").all()
    serializer_class = ItemPecaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.tipo == Usuario.Tipo.MECANICO:
            return queryset.filter(ordem_servico__mecanico=self.request.user)
        return queryset

    def get_permissions(self):
        return [IsEquipeOficina()]

    def perform_destroy(self, instance):
        excluir_item_peca(item=instance, responsavel=self.request.user)
