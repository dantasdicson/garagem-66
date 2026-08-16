from django.conf import settings
from django.db import models

from .ordem_servico import OrdemServico


class HistoricoStatusOrdem(models.Model):
    ordem_servico = models.ForeignKey(
        "oficina.OrdemServico",
        on_delete=models.CASCADE,
        related_name="historico_status",
    )
    status_anterior = models.CharField(max_length=30, choices=OrdemServico.Status.choices)
    novo_status = models.CharField(max_length=30, choices=OrdemServico.Status.choices)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="alteracoes_status_ordem",
        null=True,
    )
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "histórico de status da ordem"
        verbose_name_plural = "históricos de status das ordens"
        ordering = ("-criado_em", "-id")

    def __str__(self):
        return f"{self.ordem_servico.numero}: {self.status_anterior} → {self.novo_status}"
