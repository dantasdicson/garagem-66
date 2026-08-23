from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import Orcamento
from ..services import emitir_orcamento
from .item_orcamento_peca import ItemOrcamentoPecaSerializer
from .item_orcamento_servico import ItemOrcamentoServicoSerializer


class OrcamentoSerializer(serializers.ModelSerializer):
    valor_mao_obra = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0"), required=True)
    valor_pecas = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0"), required=True)
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    servicos_previstos = ItemOrcamentoServicoSerializer(many=True, read_only=True)
    pecas_previstas = ItemOrcamentoPecaSerializer(many=True, read_only=True)

    class Meta:
        model = Orcamento
        fields = "__all__"
        read_only_fields = (
            "id", "status", "criado_em", "atualizado_em", "emitido_por",
            "decidido_em", "decidido_por", "publicado_em", "publicado_por",
        )

    def validate(self, attrs):
        if self.instance and self.instance.status != Orcamento.Status.RASCUNHO:
            raise serializers.ValidationError("Somente um orçamento em rascunho pode ser alterado.")
        if not self.instance:
            valor_mao_obra = attrs.get("valor_mao_obra", Decimal("0"))
            valor_pecas = attrs.get("valor_pecas", Decimal("0"))
            if valor_mao_obra + valor_pecas <= 0:
                raise serializers.ValidationError({"valor_total": "Informe um valor total maior que zero."})
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
