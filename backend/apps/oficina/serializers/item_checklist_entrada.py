from rest_framework import serializers

from ..models import ItemChecklistEntrada


class ItemChecklistEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemChecklistEntrada
        fields = "__all__"
        read_only_fields = ("id",)

    def validate(self, attrs):
        item = attrs.get("item", getattr(self.instance, "item", None))
        estado = attrs.get("estado", getattr(self.instance, "estado", ""))
        percentual = attrs.get("percentual", getattr(self.instance, "percentual", None))
        itens_percentuais = {
            ItemChecklistEntrada.Item.PNEU_DIANTEIRO,
            ItemChecklistEntrada.Item.PNEU_TRASEIRO,
        }
        if item in itens_percentuais and (percentual is None or not 0 <= percentual <= 100):
            raise serializers.ValidationError({"percentual": "Informe um valor entre 0 e 100 para o pneu."})
        if item not in itens_percentuais and not estado:
            raise serializers.ValidationError({"estado": "Informe o estado deste item do checklist."})
        return attrs
