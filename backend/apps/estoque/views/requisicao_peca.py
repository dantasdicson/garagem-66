from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.usuarios.models import Usuario
from apps.usuarios.permissions import IsAdministrador, IsEquipeOficina, IsMecanico

from ..models import RequisicaoPeca
from ..serializers import RequisicaoPecaSerializer
from ..services import decidir_requisicao_peca

class RequisicaoPecaViewSet(ModelViewSet):
    queryset = RequisicaoPeca.objects.select_related("ordem_servico", "mecanico", "peca", "decidida_por").all()
    serializer_class = RequisicaoPecaSerializer
    http_method_names = ("get", "post", "head", "options")

    def get_permissions(self):
        if self.action == "create":
            return [IsMecanico()]
        if self.action in {"aprovar", "recusar"}:
            return [IsAdministrador()]
        return [IsEquipeOficina()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.tipo == Usuario.Tipo.MECANICO:
            return queryset.filter(mecanico=self.request.user)
        return queryset

    def _decidir(self, request, novo_status):
        try:
            requisicao = decidir_requisicao_peca(
                requisicao=self.get_object(),
                administrador=request.user,
                novo_status=novo_status,
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
        return Response(self.get_serializer(requisicao).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=("post",))
    def aprovar(self, request, pk=None):
        return self._decidir(request, RequisicaoPeca.Status.APROVADA)

    @action(detail=True, methods=("post",))
    def recusar(self, request, pk=None):
        return self._decidir(request, RequisicaoPeca.Status.RECUSADA)
