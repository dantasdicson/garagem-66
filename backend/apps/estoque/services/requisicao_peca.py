from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.usuarios.models import Usuario

from ..models import ItemPeca, Peca, RequisicaoPeca


@transaction.atomic
def criar_requisicao_peca(*, ordem_servico, mecanico, peca, quantidade, observacoes=""):
    if mecanico.tipo != Usuario.Tipo.MECANICO:
        raise ValidationError({"mecanico": "Somente um mecânico pode criar uma requisição."})
    if ordem_servico.mecanico_id != mecanico.id:
        raise ValidationError({"ordem_servico": "O mecânico deve estar atribuído à ordem de serviço."})
    if quantidade <= 0:
        raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})

    return RequisicaoPeca.objects.create(
        ordem_servico=ordem_servico,
        mecanico=mecanico,
        peca=peca,
        quantidade=quantidade,
        observacoes=observacoes,
    )


@transaction.atomic
def decidir_requisicao_peca(*, requisicao, administrador, novo_status):
    if administrador.tipo != Usuario.Tipo.ADMINISTRADOR:
        raise ValidationError({"administrador": "Somente um administrador pode decidir a requisição."})
    if novo_status not in {RequisicaoPeca.Status.APROVADA, RequisicaoPeca.Status.RECUSADA}:
        raise ValidationError({"status": "A decisão deve ser aprovação ou recusa."})

    requisicao_bloqueada = RequisicaoPeca.objects.select_for_update().get(pk=requisicao.pk)
    if requisicao_bloqueada.status != RequisicaoPeca.Status.PENDENTE:
        raise ValidationError({"status": "Esta requisição já foi decidida."})

    if novo_status == RequisicaoPeca.Status.APROVADA:
        peca_bloqueada = Peca.objects.select_for_update().get(pk=requisicao_bloqueada.peca_id)
        if peca_bloqueada.quantidade_estoque < requisicao_bloqueada.quantidade:
            raise ValidationError({
                "quantidade": (
                    f"Estoque insuficiente para aprovação. Disponível: "
                    f"{peca_bloqueada.quantidade_estoque}."
                )
            })
        ItemPeca.objects.create(
            ordem_servico=requisicao_bloqueada.ordem_servico,
            requisicao_peca=requisicao_bloqueada,
            peca=peca_bloqueada,
            quantidade=requisicao_bloqueada.quantidade,
            valor_unitario=peca_bloqueada.valor_unitario,
        )
        peca_bloqueada.quantidade_estoque -= requisicao_bloqueada.quantidade
        peca_bloqueada.save(update_fields=("quantidade_estoque",))

    requisicao_bloqueada.status = novo_status
    requisicao_bloqueada.decidida_por = administrador
    requisicao_bloqueada.decidida_em = timezone.now()
    requisicao_bloqueada.save(update_fields=("status", "decidida_por", "decidida_em"))
    return requisicao_bloqueada
