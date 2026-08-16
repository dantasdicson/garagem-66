from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import Peca, RequisicaoPeca
from ..services import criar_requisicao_peca

class RequisicaoPecaSerializer(serializers.ModelSerializer):
    peca = serializers.PrimaryKeyRelatedField(queryset=Peca.objects.all(), required=True, allow_null=False)
    quantidade = serializers.IntegerField(min_value=1)

    class Meta:
        model = RequisicaoPeca
        fields = "__all__"
        read_only_fields = ("id", "mecanico", "status", "criada_em", "decidida_em", "decidida_por")

    def create(self, validated_data):
        try:
            return criar_requisicao_peca(
                mecanico=self.context["request"].user,
                **validated_data,
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
