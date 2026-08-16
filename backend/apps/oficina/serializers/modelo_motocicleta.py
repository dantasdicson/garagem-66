from rest_framework import serializers

from ..models import ModeloMotocicleta


class ModeloMotocicletaSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="get_categoria_display", read_only=True)

    class Meta:
        model = ModeloMotocicleta
        fields = "__all__"
        read_only_fields = ("id",)
