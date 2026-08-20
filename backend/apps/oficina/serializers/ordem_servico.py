from rest_framework import serializers

from apps.usuarios.models import Usuario
from ..models import Cliente, Motocicleta, OrdemServico
from ..services import abrir_ordem_servico, iniciar_atendimento
from .entrada_veiculo import AcessorioEntradaSerializer, AvariaEntradaSerializer, ItemChecklistEntradaAninhadoSerializer


class AcaoStatusOrdemSerializer(serializers.Serializer):
    observacao = serializers.CharField(required=False, allow_blank=True, default="")


class ReabrirOrdemSerializer(serializers.Serializer):
    observacao = serializers.CharField(required=True, allow_blank=False)


class AbrirAtendimentoSerializer(serializers.Serializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    motocicleta = serializers.PrimaryKeyRelatedField(queryset=Motocicleta.objects.all(), required=False, allow_null=True)
    marca = serializers.CharField(max_length=80, required=False)
    modelo = serializers.CharField(max_length=100, required=False)
    ano = serializers.IntegerField(min_value=1900, max_value=2100, required=False)
    placa = serializers.CharField(max_length=10, required=False)
    chassi = serializers.CharField(max_length=30, required=False, allow_blank=True, allow_null=True)
    cor = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    mecanico = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.filter(tipo=Usuario.Tipo.MECANICO), required=False, allow_null=True)
    tipo_manutencao = serializers.ChoiceField(choices=OrdemServico.TipoManutencao.choices)
    descricao_problema = serializers.CharField()
    quilometragem = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    nivel_combustivel = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    motivo_entrada = serializers.CharField()
    observacoes = serializers.CharField(required=False, allow_blank=True, default="")
    itens_checklist = ItemChecklistEntradaAninhadoSerializer(many=True)
    avarias = AvariaEntradaSerializer(many=True, required=False, default=list)
    acessorios = AcessorioEntradaSerializer(many=True, required=False, default=list)

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

    def validate(self, attrs):
        motocicleta = attrs.get("motocicleta")
        if motocicleta and motocicleta.cliente_id != attrs["cliente"].id:
            raise serializers.ValidationError({"motocicleta": "A motocicleta não pertence ao cliente informado."})
        if not motocicleta:
            faltantes = [campo for campo in ("marca", "modelo", "ano", "placa") if not attrs.get(campo)]
            if faltantes:
                raise serializers.ValidationError({campo: "Campo obrigatório para uma nova motocicleta." for campo in faltantes})
        return attrs

    def create(self, validated_data):
        cliente = validated_data.pop("cliente")
        motocicleta = validated_data.pop("motocicleta", None)
        campos_moto = ("marca", "modelo", "ano", "placa", "chassi", "cor")
        dados_motocicleta = {campo: validated_data.pop(campo, None) for campo in campos_moto} if motocicleta is None else None
        if motocicleta is not None:
            for campo in campos_moto:
                validated_data.pop(campo, None)
        campos_entrada = ("quilometragem", "nivel_combustivel", "motivo_entrada", "observacoes", "itens_checklist", "avarias", "acessorios")
        dados_entrada = {campo: validated_data.pop(campo) for campo in campos_entrada}
        ordem, _ = iniciar_atendimento(
            cliente=cliente, responsavel=self.context["request"].user, motocicleta=motocicleta,
            dados_motocicleta=dados_motocicleta, dados_ordem=validated_data, dados_entrada=dados_entrada,
        )
        return ordem


class OrdemServicoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True)
    motocicleta_descricao = serializers.SerializerMethodField()
    mecanico_nome = serializers.CharField(source="mecanico.get_full_name", read_only=True)

    def get_motocicleta_descricao(self, obj):
        return str(obj.motocicleta)

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
