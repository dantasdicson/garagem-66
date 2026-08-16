from django.db import models


class ItemOrcamentoPeca(models.Model):
    orcamento = models.ForeignKey(
        "oficina.Orcamento",
        on_delete=models.CASCADE,
        related_name="pecas_previstas",
    )
    peca = models.ForeignKey(
        "estoque.Peca",
        on_delete=models.PROTECT,
        related_name="itens_orcamento",
    )
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "peça prevista no orçamento"
        verbose_name_plural = "peças previstas no orçamento"

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario

    def __str__(self):
        return f"{self.peca} ({self.quantidade})"
