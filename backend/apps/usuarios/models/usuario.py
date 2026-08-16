from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Tipo(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        ATENDENTE = "ATENDENTE", "Atendente"
        MECANICO = "MECANICO", "Mecânico"
        CLIENTE = "CLIENTE", "Cliente"

    email = models.EmailField("e-mail", unique=True)
    tipo = models.CharField("perfil", max_length=20, choices=Tipo.choices)
    deve_alterar_senha = models.BooleanField(default=False)

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    def __str__(self):
        return self.get_full_name() or self.username
