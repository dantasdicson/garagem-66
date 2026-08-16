from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import ItemOrcamentoPeca
from ..services import adicionar_peca_prevista


class ItemOrcamentoPecaSerializer(serializers.ModelSerializer):
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    peca_nome = serializers.CharField(source="peca.nome", read_only=True)
    peca_codigo = serializers.CharField(source="peca.codigo", read_only=True)

    class Meta:
        model = ItemOrcamentoPeca
        fields = "__all__"
        read_only_fields = ("id",)

    def create(self, validated_data):
        try:
            return adicionar_peca_prevista(
                responsavel=self.context["request"].user,
                **validated_data,
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
