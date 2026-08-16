from django.db import models


class Motocicleta(models.Model):
    cliente = models.ForeignKey("oficina.Cliente", on_delete=models.PROTECT, related_name="motocicletas")
    marca = models.CharField(max_length=80)
    modelo = models.CharField(max_length=100)
    ano = models.PositiveSmallIntegerField()
    placa = models.CharField(max_length=10, unique=True)
    chassi = models.CharField(max_length=30, unique=True, null=True, blank=True)
    cor = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "motocicleta"
        verbose_name_plural = "motocicletas"
        ordering = ("placa",)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"
