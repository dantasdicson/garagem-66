from rest_framework.viewsets import ModelViewSet
from ..models import Peca
from ..serializers import PecaSerializer
from apps.usuarios.permissions import IsEquipeOficina, PodeGerenciarOperacao

class PecaViewSet(ModelViewSet):
    queryset = Peca.objects.all()
    serializer_class = PecaSerializer

    def get_permissions(self):
        return [(PodeGerenciarOperacao if self.request.method not in ("GET", "HEAD", "OPTIONS") else IsEquipeOficina)()]
