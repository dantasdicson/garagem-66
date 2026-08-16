from django.core.exceptions import ValidationError
from django.db import transaction

from apps.oficina.models import OrdemServico
from apps.oficina.services import validar_execucao_ordem

from ..models import ItemPeca, Peca


@transaction.atomic
def registrar_item_peca(*, ordem_servico, responsavel, peca, quantidade, valor_unitario, requisicao_peca=None):
    if quantidade <= 0:
        raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})

    ordem_bloqueada = OrdemServico.objects.select_for_update().select_related("mecanico", "orcamento").get(
        pk=ordem_servico.pk
    )
    validar_execucao_ordem(ordem_servico=ordem_bloqueada, responsavel=responsavel)
    peca_bloqueada = Peca.objects.select_for_update().get(pk=peca.pk)
    if peca_bloqueada.quantidade_estoque < quantidade:
        raise ValidationError(
            {"quantidade": f"Estoque insuficiente. Disponível: {peca_bloqueada.quantidade_estoque}."}
        )

    item = ItemPeca.objects.create(
        ordem_servico=ordem_bloqueada,
        requisicao_peca=requisicao_peca,
        peca=peca_bloqueada,
        quantidade=quantidade,
        valor_unitario=valor_unitario,
    )
    peca_bloqueada.quantidade_estoque -= quantidade
    peca_bloqueada.save(update_fields=("quantidade_estoque",))
    return item


@transaction.atomic
def excluir_item_peca(*, item, responsavel):
    item_bloqueado = ItemPeca.objects.select_for_update().get(pk=item.pk)
    ordem_bloqueada = OrdemServico.objects.select_for_update().select_related("mecanico", "orcamento").get(
        pk=item_bloqueado.ordem_servico_id
    )
    validar_execucao_ordem(ordem_servico=ordem_bloqueada, responsavel=responsavel)
    peca_bloqueada = Peca.objects.select_for_update().get(pk=item_bloqueado.peca_id)
    peca_bloqueada.quantidade_estoque += item_bloqueado.quantidade
    peca_bloqueada.save(update_fields=("quantidade_estoque",))
    item_bloqueado.delete()
