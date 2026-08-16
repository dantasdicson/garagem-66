from rest_framework import serializers

from ..models import OrdemServico
from apps.usuarios.models import Usuario


class AcaoStatusOrdemSerializer(serializers.Serializer):
    observacao = serializers.CharField(required=False, allow_blank=True, default="")


class ReabrirOrdemSerializer(serializers.Serializer):
    observacao = serializers.CharField(required=True, allow_blank=False)


class OrdemServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdemServico
        fields = "__all__"
        read_only_fields = ("id", "status", "aberta_em", "atualizada_em", "concluida_em")

    def validate(self, attrs):
        motocicleta = attrs.get("motocicleta", getattr(self.instance, "motocicleta", None))
        cliente = attrs.get("cliente", getattr(self.instance, "cliente", None))
        if motocicleta and cliente and motocicleta.cliente_id != cliente.id:
            raise serializers.ValidationError({"cliente": "O cliente deve ser o proprietário da motocicleta."})
        mecanico = attrs.get("mecanico", getattr(self.instance, "mecanico", None))
        if mecanico and mecanico.tipo != Usuario.Tipo.MECANICO:
            raise serializers.ValidationError({"mecanico": "O responsável deve possuir o perfil de mecânico."})
        return attrs
