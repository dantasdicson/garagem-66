from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.usuarios.models import Usuario
from apps.usuarios.permissions import SenhaAtualizada

from ..models import HistoricoStatusOrdem
from ..serializers import HistoricoStatusOrdemSerializer


class HistoricoStatusOrdemViewSet(ReadOnlyModelViewSet):
    queryset = HistoricoStatusOrdem.objects.select_related("ordem_servico", "responsavel").all()
    serializer_class = HistoricoStatusOrdemSerializer
    permission_classes = (SenhaAtualizada,)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.tipo == Usuario.Tipo.MECANICO:
            queryset = queryset.filter(ordem_servico__mecanico=self.request.user)
        if self.request.user.tipo == Usuario.Tipo.CLIENTE:
            queryset = queryset.filter(ordem_servico__cliente__usuario=self.request.user)
        ordem_id = self.request.query_params.get("ordem_servico")
        if ordem_id:
            queryset = queryset.filter(ordem_servico_id=ordem_id)
        return queryset
