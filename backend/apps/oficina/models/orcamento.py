from django.db import models


class Orcamento(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = "RASCUNHO", "Rascunho aguardando publicação"
        AGUARDANDO_APROVACAO = "AGUARDANDO_APROVACAO", "Aguardando aprovação"
        APROVADO = "APROVADO", "Aprovado"
        RECUSADO = "RECUSADO", "Recusado"

    ordem_servico = models.OneToOneField("oficina.OrdemServico", on_delete=models.CASCADE, related_name="orcamento")
    valor_mao_obra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_pecas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True)
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.RASCUNHO,
    )
    validade = models.DateField(null=True, blank=True)
    decidido_em = models.DateTimeField(null=True, blank=True)
    decidido_por = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.PROTECT,
        related_name="orcamentos_decididos",
        null=True,
        blank=True,
    )
    emitido_por = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.PROTECT,
        related_name="orcamentos_emitidos",
        null=True,
        blank=True,
    )
    publicado_em = models.DateTimeField(null=True, blank=True)
    publicado_por = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.PROTECT,
        related_name="orcamentos_publicados",
        null=True,
        blank=True,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "orçamento"
        verbose_name_plural = "orçamentos"

    @property
    def valor_total(self):
        return self.valor_mao_obra + self.valor_pecas

    def __str__(self):
        return f"Orçamento {self.ordem_servico.numero}"
