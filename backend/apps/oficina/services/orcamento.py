from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.usuarios.models import Usuario

from ..models import ItemOrcamentoPeca, ItemOrcamentoServico, Orcamento, OrdemServico
from .status_ordem import alterar_status_ordem


def _validar_responsavel_orcamento(responsavel):
    if responsavel.tipo not in {Usuario.Tipo.ADMINISTRADOR, Usuario.Tipo.ATENDENTE}:
        raise ValidationError({"responsavel": "Somente administrador ou atendente pode alterar o orçamento."})


def _obter_orcamento_editavel(orcamento):
    orcamento_bloqueado = Orcamento.objects.select_for_update().get(pk=orcamento.pk)
    if orcamento_bloqueado.status != Orcamento.Status.AGUARDANDO_APROVACAO:
        raise ValidationError({"orcamento": "Um orçamento já decidido não pode ser alterado."})
    return orcamento_bloqueado


def _recalcular_totais(orcamento):
    valor_servicos = sum((item.valor_total for item in orcamento.servicos_previstos.all()), Decimal("0"))
    valor_pecas = sum((item.valor_total for item in orcamento.pecas_previstas.all()), Decimal("0"))
    orcamento.valor_mao_obra = valor_servicos
    orcamento.valor_pecas = valor_pecas
    orcamento.save(update_fields=("valor_mao_obra", "valor_pecas", "atualizado_em"))


@transaction.atomic
def emitir_orcamento(
    *,
    ordem_servico,
    emitido_por,
    valor_mao_obra=Decimal("0"),
    valor_pecas=Decimal("0"),
    observacoes="",
    validade=None,
):
    if emitido_por.tipo not in {Usuario.Tipo.ADMINISTRADOR, Usuario.Tipo.ATENDENTE}:
        raise ValidationError({"emitido_por": "Somente administrador ou atendente pode emitir orçamento."})

    ordem_bloqueada = OrdemServico.objects.select_for_update().get(pk=ordem_servico.pk)
    estados_permitidos = {OrdemServico.Status.ABERTA, OrdemServico.Status.AGUARDANDO_ORCAMENTO}
    if ordem_bloqueada.status not in estados_permitidos:
        raise ValidationError({"ordem_servico": "A ordem de serviço não está aguardando orçamento."})
    if Orcamento.objects.filter(ordem_servico=ordem_bloqueada).exists():
        raise ValidationError({"ordem_servico": "Esta ordem de serviço já possui orçamento."})

    orcamento = Orcamento.objects.create(
        ordem_servico=ordem_bloqueada,
        emitido_por=emitido_por,
        valor_mao_obra=valor_mao_obra,
        valor_pecas=valor_pecas,
        observacoes=observacoes,
        validade=validade or timezone.localdate() + timedelta(days=7),
    )
    alterar_status_ordem(
        ordem_servico=ordem_bloqueada,
        novo_status=OrdemServico.Status.AGUARDANDO_APROVACAO,
        responsavel=emitido_por,
        observacao="Orçamento emitido e enviado para decisão do cliente.",
    )
    return orcamento


@transaction.atomic
def decidir_orcamento(*, orcamento, cliente_usuario, novo_status):
    if cliente_usuario.tipo != Usuario.Tipo.CLIENTE:
        raise ValidationError({"cliente": "Somente o cliente pode decidir o orçamento."})
    if novo_status not in {Orcamento.Status.APROVADO, Orcamento.Status.RECUSADO}:
        raise ValidationError({"status": "A decisão deve ser aprovação ou recusa."})

    orcamento_bloqueado = (
        Orcamento.objects.select_for_update()
        .select_related("ordem_servico__cliente")
        .get(pk=orcamento.pk)
    )
    ordem_bloqueada = OrdemServico.objects.select_for_update().get(pk=orcamento_bloqueado.ordem_servico_id)

    if ordem_bloqueada.cliente.usuario_id != cliente_usuario.id:
        raise ValidationError({"cliente": "Este orçamento não pertence ao cliente autenticado."})
    if orcamento_bloqueado.status != Orcamento.Status.AGUARDANDO_APROVACAO:
        raise ValidationError({"status": "Este orçamento já foi decidido."})
    if orcamento_bloqueado.validade and orcamento_bloqueado.validade < timezone.localdate():
        raise ValidationError({"validade": "Este orçamento está vencido."})

    agora = timezone.now()
    orcamento_bloqueado.status = novo_status
    orcamento_bloqueado.decidido_por = cliente_usuario
    orcamento_bloqueado.decidido_em = agora
    orcamento_bloqueado.save(update_fields=("status", "decidido_por", "decidido_em", "atualizado_em"))

    if novo_status == Orcamento.Status.APROVADO:
        novo_status_ordem = OrdemServico.Status.EM_EXECUCAO
        ordem_bloqueada.concluida_em = None
    else:
        novo_status_ordem = OrdemServico.Status.CONCLUIDA_NAO_APROVADA
        ordem_bloqueada.concluida_em = agora
    ordem_bloqueada.save(update_fields=("concluida_em", "atualizada_em"))
    alterar_status_ordem(
        ordem_servico=ordem_bloqueada,
        novo_status=novo_status_ordem,
        responsavel=cliente_usuario,
        observacao=f"Orçamento {orcamento_bloqueado.get_status_display().lower()} pelo cliente.",
    )
    return orcamento_bloqueado


@transaction.atomic
def adicionar_servico_previsto(*, orcamento, responsavel, descricao, quantidade, valor_unitario):
    _validar_responsavel_orcamento(responsavel)
    if quantidade <= 0:
        raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})
    orcamento_bloqueado = _obter_orcamento_editavel(orcamento)
    item = ItemOrcamentoServico.objects.create(
        orcamento=orcamento_bloqueado,
        descricao=descricao,
        quantidade=quantidade,
        valor_unitario=valor_unitario,
    )
    _recalcular_totais(orcamento_bloqueado)
    return item


@transaction.atomic
def adicionar_peca_prevista(*, orcamento, responsavel, peca, quantidade, valor_unitario):
    _validar_responsavel_orcamento(responsavel)
    if quantidade <= 0:
        raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})
    orcamento_bloqueado = _obter_orcamento_editavel(orcamento)
    item = ItemOrcamentoPeca.objects.create(
        orcamento=orcamento_bloqueado,
        peca=peca,
        quantidade=quantidade,
        valor_unitario=valor_unitario,
    )
    _recalcular_totais(orcamento_bloqueado)
    return item


@transaction.atomic
def remover_item_previsto(*, item, responsavel):
    _validar_responsavel_orcamento(responsavel)
    orcamento_bloqueado = _obter_orcamento_editavel(item.orcamento)
    item.delete()
    _recalcular_totais(orcamento_bloqueado)
