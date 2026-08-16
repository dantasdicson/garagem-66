from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import Orcamento
from ..services import emitir_orcamento
from .item_orcamento_peca import ItemOrcamentoPecaSerializer
from .item_orcamento_servico import ItemOrcamentoServicoSerializer


class OrcamentoSerializer(serializers.ModelSerializer):
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    servicos_previstos = ItemOrcamentoServicoSerializer(many=True, read_only=True)
    pecas_previstas = ItemOrcamentoPecaSerializer(many=True, read_only=True)

    class Meta:
        model = Orcamento
        fields = "__all__"
        read_only_fields = (
            "id", "status", "valor_mao_obra", "valor_pecas", "criado_em", "atualizado_em", "emitido_por",
            "decidido_em", "decidido_por",
        )

    def validate(self, attrs):
        if self.instance and self.instance.status != Orcamento.Status.AGUARDANDO_APROVACAO:
            raise serializers.ValidationError("Um orçamento já decidido não pode ser alterado.")
        return attrs

    def create(self, validated_data):
        try:
            return emitir_orcamento(
                emitido_por=self.context["request"].user,
                **validated_data,
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
