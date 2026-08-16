from rest_framework import serializers

from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import Acessorio, Avaria, EntradaVeiculo, ItemChecklistEntrada
from ..services import registrar_entrada_veiculo


class ItemChecklistEntradaAninhadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemChecklistEntrada
        exclude = ("entrada_veiculo",)
        read_only_fields = ("id",)


class AvariaEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaria
        exclude = ("entrada_veiculo",)
        read_only_fields = ("id",)


class AcessorioEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acessorio
        exclude = ("entrada_veiculo",)
        read_only_fields = ("id",)


class EntradaVeiculoSerializer(serializers.ModelSerializer):
    itens_checklist = ItemChecklistEntradaAninhadoSerializer(many=True, required=False)
    avarias = AvariaEntradaSerializer(many=True, required=False)
    acessorios = AcessorioEntradaSerializer(many=True, required=False)

    class Meta:
        model = EntradaVeiculo
        fields = "__all__"
        read_only_fields = ("id", "registrada_em")

    def validate_motivo_entrada(self, valor):
        if not valor.strip():
            raise serializers.ValidationError("Informe o motivo da entrada da motocicleta.")
        return valor

    def validate(self, attrs):
        if self.instance is None and "itens_checklist" not in attrs:
            raise serializers.ValidationError({"itens_checklist": "Envie o checklist completo da entrada."})
        return attrs

    def create(self, validated_data):
        itens_checklist = validated_data.pop("itens_checklist")
        avarias = validated_data.pop("avarias", [])
        acessorios = validated_data.pop("acessorios", [])
        try:
            return registrar_entrada_veiculo(
                responsavel=self.context["request"].user,
                itens_checklist=itens_checklist,
                avarias=avarias,
                acessorios=acessorios,
                **validated_data,
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro

    def update(self, instance, validated_data):
        if any(campo in validated_data for campo in ("itens_checklist", "avarias", "acessorios")):
            raise serializers.ValidationError(
                "Checklist, avarias e acessórios não podem ser substituídos pela atualização da entrada."
            )
        return super().update(instance, validated_data)
