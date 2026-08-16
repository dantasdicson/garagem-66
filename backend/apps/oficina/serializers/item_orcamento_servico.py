from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import ItemOrcamentoServico
from ..services import adicionar_servico_previsto


class ItemOrcamentoServicoSerializer(serializers.ModelSerializer):
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ItemOrcamentoServico
        fields = "__all__"
        read_only_fields = ("id",)

    def create(self, validated_data):
        try:
            return adicionar_servico_previsto(
                responsavel=self.context["request"].user,
                **validated_data,
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
