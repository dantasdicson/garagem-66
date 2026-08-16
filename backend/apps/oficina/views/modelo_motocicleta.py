from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.usuarios.permissions import IsEquipeOficina
from ..models import ModeloMotocicleta
from ..serializers import ModeloMotocicletaSerializer


class ModeloMotocicletaViewSet(ReadOnlyModelViewSet):
    queryset = ModeloMotocicleta.objects.filter(ativo=True)
    serializer_class = ModeloMotocicletaSerializer
    permission_classes = (IsEquipeOficina,)
