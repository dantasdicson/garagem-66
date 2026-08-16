from django.core.exceptions import ValidationError
from django.db import models


class OrdemServico(models.Model):
    class TipoManutencao(models.TextChoices):
        CORRETIVA = "CORRETIVA", "Corretiva"
        PREVENTIVA = "PREVENTIVA", "Preventiva"

    class Status(models.TextChoices):
        ABERTA = "ABERTA", "Aberta"
        AGUARDANDO_ORCAMENTO = "AGUARDANDO_ORCAMENTO", "Aguardando orçamento"
        AGUARDANDO_APROVACAO = "AGUARDANDO_APROVACAO", "Aguardando aprovação"
        EM_EXECUCAO = "EM_EXECUCAO", "Em execução"
        AGUARDANDO_PECAS = "AGUARDANDO_PECAS", "Aguardando peças"
        CONCLUIDA = "CONCLUIDA", "Concluída"
        CONCLUIDA_NAO_APROVADA = "CONCLUIDA_NAO_APROVADA", "Concluída - Não aprovado"

    numero = models.CharField(max_length=20, unique=True)
    motocicleta = models.ForeignKey("oficina.Motocicleta", on_delete=models.PROTECT, related_name="ordens_servico")
    cliente = models.ForeignKey("oficina.Cliente", on_delete=models.PROTECT, related_name="ordens_servico")
    mecanico = models.ForeignKey(
        "usuarios.Usuario",
        on_delete=models.PROTECT,
        related_name="ordens_servico_atribuidas",
        null=True,
        blank=True,
    )
    tipo_manutencao = models.CharField(
        max_length=15,
        choices=TipoManutencao.choices,
        default=TipoManutencao.CORRETIVA,
    )
    descricao_problema = models.TextField()
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.ABERTA)
    aberta_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)
    concluida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "ordem de serviço"
        verbose_name_plural = "ordens de serviço"
        ordering = ("-aberta_em",)

    def clean(self):
        if self.motocicleta_id and self.cliente_id and self.motocicleta.cliente_id != self.cliente_id:
            raise ValidationError({"cliente": "O cliente deve ser o proprietário da motocicleta."})

    def __str__(self):
        return self.numero
