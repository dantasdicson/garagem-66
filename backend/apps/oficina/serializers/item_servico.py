from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import ItemServico
from ..services import registrar_item_servico, validar_execucao_ordem


class ItemServicoSerializer(serializers.ModelSerializer):
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ItemServico
        fields = "__all__"
        read_only_fields = ("id",)

    def validate(self, attrs):
        if self.instance:
            try:
                validar_execucao_ordem(
                    ordem_servico=self.instance.ordem_servico,
                    responsavel=self.context["request"].user,
                )
            except DjangoValidationError as erro:
                detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
                raise serializers.ValidationError(detalhes) from erro
        return attrs

    def create(self, validated_data):
        try:
            return registrar_item_servico(
                responsavel=self.context["request"].user,
                **validated_data,
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
