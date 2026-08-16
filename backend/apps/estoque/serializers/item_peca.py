from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import ItemPeca
from ..services import registrar_item_peca
from apps.oficina.services import validar_execucao_ordem

class ItemPecaSerializer(serializers.ModelSerializer):
    valor_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ItemPeca
        fields = "__all__"
        read_only_fields = ("id",)

    def validate(self, attrs):
        requisicao = attrs.get("requisicao_peca", getattr(self.instance, "requisicao_peca", None))
        ordem = attrs.get("ordem_servico", getattr(self.instance, "ordem_servico", None))
        if requisicao and ordem and requisicao.ordem_servico_id != ordem.id:
            raise serializers.ValidationError({"requisicao_peca": "A requisição deve pertencer à mesma ordem de serviço."})

        if self.instance:
            try:
                validar_execucao_ordem(
                    ordem_servico=self.instance.ordem_servico,
                    responsavel=self.context["request"].user,
                )
            except DjangoValidationError as erro:
                detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
                raise serializers.ValidationError(detalhes) from erro
            campos_imutaveis = ("ordem_servico", "requisicao_peca", "peca", "quantidade")
            alterados = [
                campo for campo in campos_imutaveis
                if campo in attrs and attrs[campo] != getattr(self.instance, campo)
            ]
            if alterados:
                raise serializers.ValidationError(
                    {campo: "Este campo não pode ser alterado após a baixa no estoque." for campo in alterados}
                )
        return attrs

    def create(self, validated_data):
        try:
            return registrar_item_peca(responsavel=self.context["request"].user, **validated_data)
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
