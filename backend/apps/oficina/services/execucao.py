from django.core.exceptions import ValidationError

from apps.usuarios.models import Usuario

from ..models import Orcamento, OrdemServico


def validar_execucao_ordem(*, ordem_servico, responsavel):
    if responsavel.tipo not in {
        Usuario.Tipo.ADMINISTRADOR,
        Usuario.Tipo.ATENDENTE,
        Usuario.Tipo.MECANICO,
    }:
        raise ValidationError({"responsavel": "Este perfil não pode registrar a execução da ordem."})

    if responsavel.tipo == Usuario.Tipo.MECANICO and ordem_servico.mecanico_id != responsavel.id:
        raise ValidationError({"responsavel": "O mecânico só pode alterar ordens atribuídas a ele."})

    estados_permitidos = {OrdemServico.Status.EM_EXECUCAO, OrdemServico.Status.AGUARDANDO_PECAS}
    if ordem_servico.status not in estados_permitidos:
        raise ValidationError({"ordem_servico": "A ordem de serviço ainda não está autorizada para execução."})

    try:
        orcamento = ordem_servico.orcamento
    except Orcamento.DoesNotExist as erro:
        raise ValidationError({"ordem_servico": "A ordem de serviço não possui orçamento aprovado."}) from erro
    if orcamento.status != Orcamento.Status.APROVADO:
        raise ValidationError({"ordem_servico": "O orçamento precisa estar aprovado antes da execução."})


