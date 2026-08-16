from rest_framework import serializers

from ..models import Motocicleta


class MotocicletaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motocicleta
        fields = "__all__"
        read_only_fields = ("id",)
