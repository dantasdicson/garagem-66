from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from apps.usuarios.models import Usuario
from apps.usuarios.permissions import PodeGerenciarOperacao, SenhaAtualizada

from ..models import ItemOrcamentoServico
from ..serializers import ItemOrcamentoServicoSerializer
from ..services import remover_item_previsto


class ItemOrcamentoServicoViewSet(ModelViewSet):
    queryset = ItemOrcamentoServico.objects.select_related("orcamento__ordem_servico__cliente").all()
    serializer_class = ItemOrcamentoServicoSerializer
    http_method_names = ("get", "post", "delete", "head", "options")

    def get_permissions(self):
        return [SenhaAtualizada()] if self.request.method in ("GET", "HEAD", "OPTIONS") else [PodeGerenciarOperacao()]

    def get_queryset(self):
        queryset = super().get_queryset()
        usuario = self.request.user
        if usuario.tipo == Usuario.Tipo.CLIENTE:
            return queryset.filter(orcamento__ordem_servico__cliente__usuario=usuario)
        if usuario.tipo == Usuario.Tipo.MECANICO:
            return queryset.filter(orcamento__ordem_servico__mecanico=usuario)
        return queryset

    def perform_destroy(self, instance):
        try:
            remover_item_previsto(item=instance, responsavel=self.request.user)
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
