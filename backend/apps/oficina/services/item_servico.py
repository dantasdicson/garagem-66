from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import ItemServico, OrdemServico
from .execucao import validar_execucao_ordem


@transaction.atomic
def registrar_item_servico(*, ordem_servico, responsavel, descricao, quantidade, valor_unitario):
    ordem_bloqueada = OrdemServico.objects.select_for_update().select_related("mecanico", "orcamento").get(
        pk=ordem_servico.pk
    )
    validar_execucao_ordem(ordem_servico=ordem_bloqueada, responsavel=responsavel)
    if not descricao.strip():
        raise ValidationError({"descricao": "Informe o serviço executado."})
    if quantidade <= 0:
        raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})
    return ItemServico.objects.create(
        ordem_servico=ordem_bloqueada,
        descricao=descricao,
        quantidade=quantidade,
        valor_unitario=valor_unitario,
    )


