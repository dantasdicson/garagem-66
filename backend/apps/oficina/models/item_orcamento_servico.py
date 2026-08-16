from django.db import models


class ItemOrcamentoServico(models.Model):
    orcamento = models.ForeignKey(
        "oficina.Orcamento",
        on_delete=models.CASCADE,
        related_name="servicos_previstos",
    )
    descricao = models.CharField(max_length=255)
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "serviço previsto no orçamento"
        verbose_name_plural = "serviços previstos no orçamento"

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario

    def __str__(self):
        return self.descricao
