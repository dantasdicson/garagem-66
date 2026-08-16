from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from ..models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = (
            "id", "username", "email", "first_name", "last_name", "tipo",
            "is_active", "deve_alterar_senha", "password",
        )
        read_only_fields = ("id", "deve_alterar_senha")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        usuario = Usuario(**validated_data)
        if password:
            usuario.set_password(password)
        else:
            usuario.set_unusable_password()
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
