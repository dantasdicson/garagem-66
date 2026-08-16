from rest_framework.viewsets import ModelViewSet
from ..models import Acessorio
from ..serializers import AcessorioSerializer
from apps.usuarios.permissions import IsEquipeOficina, PodeGerenciarOperacao

class AcessorioViewSet(ModelViewSet):
    queryset = Acessorio.objects.select_related("entrada_veiculo").all()
    serializer_class = AcessorioSerializer

    def get_permissions(self):
        return [(PodeGerenciarOperacao if self.request.method not in ("GET", "HEAD", "OPTIONS") else IsEquipeOficina)()]
