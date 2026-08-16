from django.db import models


class ItemPeca(models.Model):
    ordem_servico = models.ForeignKey("oficina.OrdemServico", on_delete=models.CASCADE, related_name="itens_peca")
    requisicao_peca = models.ForeignKey(
        "estoque.RequisicaoPeca",
        on_delete=models.SET_NULL,
        related_name="itens",
        null=True,
        blank=True,
    )
    peca = models.ForeignKey("estoque.Peca", on_delete=models.PROTECT, related_name="itens_utilizados")
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "item de peça"
        verbose_name_plural = "itens de peça"

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario

    def __str__(self):
        return f"{self.peca} ({self.quantidade})"
