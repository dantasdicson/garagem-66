from rest_framework import serializers

from ..models import Cliente, Motocicleta, OrdemServico
from ..services import abrir_atendimento_com_motocicleta, abrir_ordem_servico
from apps.usuarios.models import Usuario


class AcaoStatusOrdemSerializer(serializers.Serializer):
    observacao = serializers.CharField(required=False, allow_blank=True, default="")


class ReabrirOrdemSerializer(serializers.Serializer):
    observacao = serializers.CharField(required=True, allow_blank=False)


class AbrirAtendimentoSerializer(serializers.Serializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    marca = serializers.CharField(max_length=80)
    modelo = serializers.CharField(max_length=100)
    ano = serializers.IntegerField(min_value=1900, max_value=2100)
    placa = serializers.CharField(max_length=10)
    chassi = serializers.CharField(max_length=30, required=False, allow_blank=True, allow_null=True)
    cor = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    mecanico = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.filter(tipo=Usuario.Tipo.MECANICO), required=False, allow_null=True)
    tipo_manutencao = serializers.ChoiceField(choices=OrdemServico.TipoManutencao.choices)
    descricao_problema = serializers.CharField()

    def validate_placa(self, valor):
        placa = valor.strip().upper()
        if Motocicleta.objects.filter(placa=placa).exists():
            raise serializers.ValidationError("Esta placa já está cadastrada; selecione a motocicleta existente.")
        return placa

    def validate_chassi(self, valor):
        chassi = valor.strip().upper() if valor else None
        if chassi and Motocicleta.objects.filter(chassi=chassi).exists():
            raise serializers.ValidationError("Este chassi já está cadastrado.")
        return chassi

    def create(self, validated_data):
        cliente = validated_data.pop("cliente")
        campos_moto = ("marca", "modelo", "ano", "placa", "chassi", "cor")
        dados_motocicleta = {campo: validated_data.pop(campo) for campo in campos_moto}
        return abrir_atendimento_com_motocicleta(
            cliente=cliente, dados_motocicleta=dados_motocicleta, dados_ordem=validated_data,
        )


class OrdemServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdemServico
        fields = "__all__"
        read_only_fields = ("id", "numero", "status", "aberta_em", "atualizada_em", "concluida_em")

    def create(self, validated_data):
        return abrir_ordem_servico(**validated_data)

    def validate(self, attrs):
        motocicleta = attrs.get("motocicleta", getattr(self.instance, "motocicleta", None))
        cliente = attrs.get("cliente", getattr(self.instance, "cliente", None))
        if motocicleta and cliente and motocicleta.cliente_id != cliente.id:
            raise serializers.ValidationError({"cliente": "O cliente deve ser o proprietário da motocicleta."})
        mecanico = attrs.get("mecanico", getattr(self.instance, "mecanico", None))
        if mecanico and mecanico.tipo != Usuario.Tipo.MECANICO:
            raise serializers.ValidationError({"mecanico": "O responsável deve possuir o perfil de mecânico."})
        return attrs
