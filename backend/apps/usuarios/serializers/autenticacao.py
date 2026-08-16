from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..services import alterar_senha


class Garagem66TokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        dados = super().validate(attrs)
        dados["usuario"] = {
            "id": self.user.id,
            "username": self.user.username,
            "nome": self.user.get_full_name(),
            "tipo": self.user.tipo,
            "deve_alterar_senha": self.user.deve_alterar_senha,
        }
        return dados


class AlterarSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True)

    def save(self, **kwargs):
        try:
            return alterar_senha(
                usuario=self.context["request"].user,
                senha_atual=self.validated_data["senha_atual"],
                nova_senha=self.validated_data["nova_senha"],
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
