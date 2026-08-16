from django.db import models


class ItemServico(models.Model):
    ordem_servico = models.ForeignKey("oficina.OrdemServico", on_delete=models.CASCADE, related_name="itens_servico")
    descricao = models.CharField(max_length=255)
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "item de serviço"
        verbose_name_plural = "itens de serviço"

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario

    def __str__(self):
        return self.descricao
