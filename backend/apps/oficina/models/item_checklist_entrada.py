from django.core.exceptions import ValidationError
from django.db import models


class ItemChecklistEntrada(models.Model):
    class Item(models.TextChoices):
        PNEU_DIANTEIRO = "PNEU_DIANTEIRO", "Pneu dianteiro"
        PNEU_TRASEIRO = "PNEU_TRASEIRO", "Pneu traseiro"
        RODAS = "RODAS", "Rodas"
        FREIOS = "FREIOS", "Freios"
        ILUMINACAO = "ILUMINACAO", "Faróis e lanternas"
        RETROVISORES = "RETROVISORES", "Retrovisores"
        CARENAGENS = "CARENAGENS", "Carenagens"
        SUSPENSAO = "SUSPENSAO", "Suspensão"
        PAINEL = "PAINEL", "Painel"

    class Estado(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        COM_AVARIA = "COM_AVARIA", "Com avaria"
        NAO_VERIFICADO = "NAO_VERIFICADO", "Não verificado"

    entrada_veiculo = models.ForeignKey(
        "oficina.EntradaVeiculo",
        on_delete=models.CASCADE,
        related_name="itens_checklist",
    )
    item = models.CharField(max_length=25, choices=Item.choices)
    estado = models.CharField(max_length=20, choices=Estado.choices, blank=True)
    percentual = models.PositiveSmallIntegerField(null=True, blank=True)
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = "item do checklist de entrada"
        verbose_name_plural = "itens do checklist de entrada"
        constraints = [
            models.UniqueConstraint(
                fields=("entrada_veiculo", "item"),
                name="checklist_item_unico_por_entrada",
            )
        ]

    def clean(self):
        itens_percentuais = {self.Item.PNEU_DIANTEIRO, self.Item.PNEU_TRASEIRO}
        if self.item in itens_percentuais:
            if self.percentual is None or not 0 <= self.percentual <= 100:
                raise ValidationError({"percentual": "Informe um valor entre 0 e 100 para o pneu."})
        elif not self.estado:
            raise ValidationError({"estado": "Informe o estado deste item do checklist."})

    def __str__(self):
        return self.get_item_display()
