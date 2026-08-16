from django.db import models


class Avaria(models.Model):
    entrada_veiculo = models.ForeignKey("oficina.EntradaVeiculo", on_delete=models.CASCADE, related_name="avarias")
    descricao = models.TextField()
    localizacao = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = "avaria"
        verbose_name_plural = "avarias"

    def __str__(self):
        return self.descricao[:50]
