from rest_framework.viewsets import ModelViewSet
from ..models import EntradaVeiculo
from ..serializers import EntradaVeiculoSerializer
from apps.usuarios.permissions import IsEquipeOficina, PodeGerenciarOperacao

class EntradaVeiculoViewSet(ModelViewSet):
    queryset = EntradaVeiculo.objects.select_related("ordem_servico").prefetch_related(
        "itens_checklist", "avarias", "acessorios"
    )
    serializer_class = EntradaVeiculoSerializer

    def get_permissions(self):
        return [(PodeGerenciarOperacao if self.request.method not in ("GET", "HEAD", "OPTIONS") else IsEquipeOficina)()]
