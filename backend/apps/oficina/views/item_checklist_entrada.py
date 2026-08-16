from rest_framework.viewsets import ModelViewSet

from apps.usuarios.permissions import IsEquipeOficina, PodeGerenciarOperacao

from ..models import ItemChecklistEntrada
from ..serializers import ItemChecklistEntradaSerializer


class ItemChecklistEntradaViewSet(ModelViewSet):
    queryset = ItemChecklistEntrada.objects.select_related("entrada_veiculo").all()
    serializer_class = ItemChecklistEntradaSerializer

    def get_permissions(self):
        permissao = PodeGerenciarOperacao if self.request.method not in ("GET", "HEAD", "OPTIONS") else IsEquipeOficina
        return [permissao()]
