from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class RequisicaoPeca(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        APROVADA = "APROVADA", "Aprovada"
        RECUSADA = "RECUSADA", "Recusada"

    ordem_servico = models.ForeignKey("oficina.OrdemServico", on_delete=models.PROTECT, related_name="requisicoes_peca")
    mecanico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="requisicoes_peca")
    peca = models.ForeignKey(
        "estoque.Peca",
        on_delete=models.PROTECT,
        related_name="requisicoes",
        null=True,
        blank=True,
    )
    quantidade = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDENTE)
    observacoes = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    decidida_em = models.DateTimeField(null=True, blank=True)
    decidida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requisicoes_peca_decididas",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "requisição de peça"
        verbose_name_plural = "requisições de peça"
        ordering = ("-criada_em",)

    def __str__(self):
        return f"Requisição {self.pk or 'nova'} - {self.ordem_servico.numero}"

    def clean(self):
        if not self.peca_id:
            raise ValidationError({"peca": "Informe a peça solicitada."})
        if self.quantidade <= 0:
            raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})
