from django.db import models


class EntradaVeiculo(models.Model):
    ordem_servico = models.OneToOneField("oficina.OrdemServico", on_delete=models.CASCADE, related_name="entrada_veiculo")
    quilometragem = models.PositiveIntegerField(null=True, blank=True)
    nivel_combustivel = models.CharField(max_length=50, blank=True)
    motivo_entrada = models.TextField(default="")
    observacoes = models.TextField(blank=True)
    registrada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "entrada de veículo"
        verbose_name_plural = "entradas de veículo"

    def __str__(self):
        return f"Entrada - {self.ordem_servico.numero}"
