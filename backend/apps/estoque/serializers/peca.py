from rest_framework import serializers
from ..models import Peca

class PecaSerializer(serializers.ModelSerializer):
    status_estoque = serializers.CharField(read_only=True)

    class Meta:
        model = Peca
        fields = "__all__"
        read_only_fields = ("id",)
