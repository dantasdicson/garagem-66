from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.usuarios.models import Usuario
from apps.usuarios.permissions import IsAdministrador, IsCliente, IsEquipeOficina, SenhaAtualizada

from ..models import Orcamento
from ..serializers import OrcamentoSerializer
from ..services import decidir_orcamento, publicar_orcamento

class OrcamentoViewSet(ModelViewSet):
    queryset = Orcamento.objects.select_related(
        "ordem_servico__cliente", "ordem_servico__motocicleta", "emitido_por", "decidido_por"
    ).all()
    serializer_class = OrcamentoSerializer
    http_method_names = ("get", "post", "put", "patch", "head", "options")

    def get_permissions(self):
        if self.action in {"aprovar", "recusar"}:
            return [IsCliente()]
        if self.action == "publicar":
            return [IsAdministrador()]
        if self.action in {"create", "update", "partial_update"}:
            return [IsEquipeOficina()]
        return [SenhaAtualizada()]

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario = self.request.user
        if usuario.tipo == Usuario.Tipo.CLIENTE:
            return queryset.filter(
                ordem_servico__cliente__usuario=usuario,
            ).exclude(status=Orcamento.Status.RASCUNHO)
        if usuario.tipo == Usuario.Tipo.MECANICO:
            return queryset.filter(ordem_servico__mecanico=usuario)
        return queryset

    def _decidir(self, request, novo_status):
        try:
            orcamento = decidir_orcamento(
                orcamento=self.get_object(),
                cliente_usuario=request.user,
                novo_status=novo_status,
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
        return Response(self.get_serializer(orcamento).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=("post",))
    def aprovar(self, request, pk=None):
        return self._decidir(request, Orcamento.Status.APROVADO)

    @action(detail=True, methods=("post",))
    def recusar(self, request, pk=None):
        return self._decidir(request, Orcamento.Status.RECUSADO)

    @action(detail=True, methods=("post",))
    def publicar(self, request, pk=None):
        try:
            orcamento = publicar_orcamento(
                orcamento=self.get_object(),
                administrador=request.user,
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
        return Response(self.get_serializer(orcamento).data, status=status.HTTP_200_OK)
