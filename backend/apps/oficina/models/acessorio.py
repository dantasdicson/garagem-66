from django.db import models


class Acessorio(models.Model):
    entrada_veiculo = models.ForeignKey("oficina.EntradaVeiculo", on_delete=models.CASCADE, related_name="acessorios")
    descricao = models.CharField(max_length=255)

    class Meta:
        verbose_name = "acessório"
        verbose_name_plural = "acessórios"

    def __str__(self):
        return self.descricao
