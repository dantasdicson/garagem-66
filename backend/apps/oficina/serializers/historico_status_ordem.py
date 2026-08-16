from rest_framework import serializers

from ..models import HistoricoStatusOrdem


class HistoricoStatusOrdemSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source="responsavel.get_full_name", read_only=True)
    status_anterior_descricao = serializers.CharField(source="get_status_anterior_display", read_only=True)
    novo_status_descricao = serializers.CharField(source="get_novo_status_display", read_only=True)

    class Meta:
        model = HistoricoStatusOrdem
        fields = "__all__"
        read_only_fields = tuple(campo.name for campo in HistoricoStatusOrdem._meta.fields)

