from rest_framework.viewsets import ModelViewSet

from ..models import Usuario
from ..permissions import IsAdministrador
from ..serializers import UsuarioSerializer


class UsuarioViewSet(ModelViewSet):
    queryset = Usuario.objects.all().order_by("username")
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdministrador]
