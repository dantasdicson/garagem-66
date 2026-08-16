from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.usuarios.models import Usuario

from ..models import HistoricoStatusOrdem, OrdemServico


TRANSICOES_PERMITIDAS = {
    OrdemServico.Status.ABERTA: {
        OrdemServico.Status.AGUARDANDO_ORCAMENTO,
        OrdemServico.Status.AGUARDANDO_APROVACAO,
    },
    OrdemServico.Status.AGUARDANDO_ORCAMENTO: {OrdemServico.Status.AGUARDANDO_APROVACAO},
    OrdemServico.Status.AGUARDANDO_APROVACAO: {
        OrdemServico.Status.EM_EXECUCAO,
        OrdemServico.Status.CONCLUIDA_NAO_APROVADA,
    },
    OrdemServico.Status.EM_EXECUCAO: {
        OrdemServico.Status.AGUARDANDO_PECAS,
        OrdemServico.Status.CONCLUIDA,
    },
    OrdemServico.Status.AGUARDANDO_PECAS: {
        OrdemServico.Status.EM_EXECUCAO,
        OrdemServico.Status.CONCLUIDA,
    },
    OrdemServico.Status.CONCLUIDA: {OrdemServico.Status.EM_EXECUCAO},
    OrdemServico.Status.CONCLUIDA_NAO_APROVADA: set(),
}


def _validar_responsavel_operacional(ordem_servico, responsavel):
    perfis_equipe = {Usuario.Tipo.ADMINISTRADOR, Usuario.Tipo.ATENDENTE, Usuario.Tipo.MECANICO}
    if responsavel.tipo not in perfis_equipe:
        raise ValidationError({"responsavel": "Somente a equipe da oficina pode alterar esta ordem."})
    if responsavel.tipo == Usuario.Tipo.MECANICO and ordem_servico.mecanico_id != responsavel.id:
        raise ValidationError({"responsavel": "O mecânico só pode alterar ordens atribuídas a ele."})


@transaction.atomic
def alterar_status_ordem(*, ordem_servico, novo_status, responsavel, observacao=""):
    if novo_status not in OrdemServico.Status.values:
        raise ValidationError({"novo_status": "Status inválido para a ordem de serviço."})

    ordem_bloqueada = OrdemServico.objects.select_for_update().get(pk=ordem_servico.pk)
    status_anterior = ordem_bloqueada.status
    if status_anterior == novo_status:
        raise ValidationError({"novo_status": "A ordem de serviço já possui este status."})
    if novo_status not in TRANSICOES_PERMITIDAS.get(status_anterior, set()):
        raise ValidationError(
            {"novo_status": f"A transição de {ordem_bloqueada.get_status_display()} para "
             f"{OrdemServico.Status(novo_status).label} não é permitida."}
        )

    ordem_bloqueada.status = novo_status
    if novo_status in {OrdemServico.Status.CONCLUIDA, OrdemServico.Status.CONCLUIDA_NAO_APROVADA}:
        ordem_bloqueada.concluida_em = timezone.now()
    elif status_anterior in {OrdemServico.Status.CONCLUIDA, OrdemServico.Status.CONCLUIDA_NAO_APROVADA}:
        ordem_bloqueada.concluida_em = None
    ordem_bloqueada.save(update_fields=("status", "concluida_em", "atualizada_em"))
    HistoricoStatusOrdem.objects.create(
        ordem_servico=ordem_bloqueada,
        status_anterior=status_anterior,
        novo_status=novo_status,
        responsavel=responsavel,
        observacao=observacao.strip(),
    )
    return ordem_bloqueada


def colocar_ordem_aguardando_pecas(*, ordem_servico, responsavel, observacao=""):
    _validar_responsavel_operacional(ordem_servico, responsavel)
    return alterar_status_ordem(
        ordem_servico=ordem_servico,
        novo_status=OrdemServico.Status.AGUARDANDO_PECAS,
        responsavel=responsavel,
        observacao=observacao or "Execução pausada aguardando peças.",
    )


def retomar_execucao_ordem(*, ordem_servico, responsavel, observacao=""):
    _validar_responsavel_operacional(ordem_servico, responsavel)
    return alterar_status_ordem(
        ordem_servico=ordem_servico,
        novo_status=OrdemServico.Status.EM_EXECUCAO,
        responsavel=responsavel,
        observacao=observacao or "Execução retomada.",
    )


def concluir_ordem(*, ordem_servico, responsavel, observacao=""):
    _validar_responsavel_operacional(ordem_servico, responsavel)
    return alterar_status_ordem(
        ordem_servico=ordem_servico,
        novo_status=OrdemServico.Status.CONCLUIDA,
        responsavel=responsavel,
        observacao=observacao or "Serviços concluídos.",
    )


def reabrir_ordem(*, ordem_servico, responsavel, observacao):
    if responsavel.tipo != Usuario.Tipo.ADMINISTRADOR:
        raise ValidationError({"responsavel": "Somente o administrador pode reabrir uma ordem."})
    if not observacao.strip():
        raise ValidationError({"observacao": "Informe a justificativa para reabrir a ordem."})
    return alterar_status_ordem(
        ordem_servico=ordem_servico,
        novo_status=OrdemServico.Status.EM_EXECUCAO,
        responsavel=responsavel,
        observacao=observacao,
    )
