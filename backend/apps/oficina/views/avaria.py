from rest_framework.viewsets import ModelViewSet
from ..models import Avaria
from ..serializers import AvariaSerializer
from apps.usuarios.permissions import IsEquipeOficina, PodeGerenciarOperacao

class AvariaViewSet(ModelViewSet):
    queryset = Avaria.objects.select_related("entrada_veiculo").all()
    serializer_class = AvariaSerializer

    def get_permissions(self):
        return [(PodeGerenciarOperacao if self.request.method not in ("GET", "HEAD", "OPTIONS") else IsEquipeOficina)()]
