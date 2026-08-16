from rest_framework import serializers

from ..models import Acessorio


class AcessorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acessorio
        fields = "__all__"
        read_only_fields = ("id",)
