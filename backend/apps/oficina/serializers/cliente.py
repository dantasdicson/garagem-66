from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import Cliente
from ..services import atualizar_cliente, cadastrar_cliente_com_acesso


class ClienteSerializer(serializers.ModelSerializer):
    cpf = serializers.CharField(required=True)
    data_nascimento = serializers.DateField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = Cliente
        fields = "__all__"
        read_only_fields = ("id", "usuario", "criado_em")

    def create(self, validated_data):
        try:
            return cadastrar_cliente_com_acesso(**validated_data)
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro

    def update(self, instance, validated_data):
        if "cpf" in validated_data and validated_data["cpf"] != instance.cpf:
            raise serializers.ValidationError({"cpf": "O CPF não pode ser alterado após o cadastro."})
        if "data_nascimento" in validated_data and validated_data["data_nascimento"] != instance.data_nascimento:
            raise serializers.ValidationError(
                {"data_nascimento": "A data de nascimento não pode ser alterada por esta operação."}
            )
        dados = {
            "nome": validated_data.get("nome", instance.nome),
            "email": validated_data.get("email", instance.email),
            "telefone": validated_data.get("telefone", instance.telefone),
            "endereco": validated_data.get("endereco", instance.endereco),
        }
        try:
            return atualizar_cliente(cliente=instance, **dados)
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
