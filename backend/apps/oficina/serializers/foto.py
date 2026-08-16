from rest_framework import serializers

from ..models import Foto


class FotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foto
        fields = "__all__"
        read_only_fields = ("id", "criada_em")
