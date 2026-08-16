from rest_framework.viewsets import ModelViewSet
from ..models import Foto
from ..serializers import FotoSerializer
from apps.usuarios.permissions import IsEquipeOficina, PodeGerenciarOperacao

class FotoViewSet(ModelViewSet):
    queryset = Foto.objects.select_related("entrada_veiculo").all()
    serializer_class = FotoSerializer

    def get_permissions(self):
        return [(PodeGerenciarOperacao if self.request.method not in ("GET", "HEAD", "OPTIONS") else IsEquipeOficina)()]
