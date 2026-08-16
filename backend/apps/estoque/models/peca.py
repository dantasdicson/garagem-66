from django.db import models


class Peca(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    quantidade_minima = models.PositiveIntegerField(default=0)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "peça"
        verbose_name_plural = "peças"
        ordering = ("nome",)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    @property
    def status_estoque(self):
        if self.quantidade_estoque == 0:
            return "INDISPONIVEL"
        if self.quantidade_estoque <= self.quantidade_minima:
            return "ESTOQUE_BAIXO"
        return "DISPONIVEL"
