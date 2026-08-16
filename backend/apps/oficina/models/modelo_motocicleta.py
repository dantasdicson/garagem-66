from django.db import models


class ModeloMotocicleta(models.Model):
    class Categoria(models.TextChoices):
        TRAIL = "TRAIL", "Trail"
        BIG_TRAIL = "BIG_TRAIL", "Big trail / Adventure"

    marca = models.CharField(max_length=80)
    modelo = models.CharField(max_length=120)
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    ativo = models.BooleanField(default=True)
    fonte_url = models.URLField(blank=True)

    class Meta:
        ordering = ("marca", "modelo")
        constraints = [models.UniqueConstraint(fields=("marca", "modelo"), name="modelo_moto_marca_modelo_unico")]

    def __str__(self):
        return f"{self.marca} {self.modelo}"
