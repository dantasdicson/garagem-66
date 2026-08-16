from django.core.exceptions import ValidationError
from django.db import transaction

from apps.usuarios.models import Usuario

from ..models import Acessorio, Avaria, EntradaVeiculo, ItemChecklistEntrada, OrdemServico
from .status_ordem import alterar_status_ordem


def _validar_checklist_completo(itens_checklist):
    itens_recebidos = [item.get("item") for item in itens_checklist]
    duplicados = sorted({item for item in itens_recebidos if itens_recebidos.count(item) > 1})
    if duplicados:
        raise ValidationError({"itens_checklist": f"Itens repetidos: {', '.join(duplicados)}."})

    itens_obrigatorios = set(ItemChecklistEntrada.Item.values)
    faltantes = sorted(itens_obrigatorios - set(itens_recebidos))
    desconhecidos = sorted(set(itens_recebidos) - itens_obrigatorios)
    erros = []
    if faltantes:
        erros.append(f"Itens obrigatórios ausentes: {', '.join(faltantes)}.")
    if desconhecidos:
        erros.append(f"Itens inválidos: {', '.join(desconhecidos)}.")
    if erros:
        raise ValidationError({"itens_checklist": erros})


@transaction.atomic
def registrar_entrada_veiculo(
    *,
    ordem_servico,
    responsavel,
    itens_checklist,
    avarias=None,
    acessorios=None,
    quilometragem=None,
    nivel_combustivel="",
    motivo_entrada="",
    observacoes="",
):
    if responsavel.tipo not in {Usuario.Tipo.ADMINISTRADOR, Usuario.Tipo.ATENDENTE}:
        raise ValidationError(
            {"responsavel": "Somente administrador ou atendente pode registrar a entrada da motocicleta."}
        )
    if not motivo_entrada.strip():
        raise ValidationError({"motivo_entrada": "Informe o motivo da entrada da motocicleta."})

    _validar_checklist_completo(itens_checklist)
    ordem_bloqueada = OrdemServico.objects.select_for_update().get(pk=ordem_servico.pk)
    if ordem_bloqueada.status != OrdemServico.Status.ABERTA:
        raise ValidationError({"ordem_servico": "A entrada só pode ser registrada para uma ordem aberta."})
    if EntradaVeiculo.objects.filter(ordem_servico=ordem_bloqueada).exists():
        raise ValidationError({"ordem_servico": "Esta ordem de serviço já possui uma entrada registrada."})

    entrada = EntradaVeiculo.objects.create(
        ordem_servico=ordem_bloqueada,
        quilometragem=quilometragem,
        nivel_combustivel=nivel_combustivel,
        motivo_entrada=motivo_entrada,
        observacoes=observacoes,
    )

    for dados in itens_checklist:
        item = ItemChecklistEntrada(entrada_veiculo=entrada, **dados)
        item.full_clean()
        item.save()

    for dados in avarias or []:
        avaria = Avaria(entrada_veiculo=entrada, **dados)
        avaria.full_clean()
        avaria.save()

    for dados in acessorios or []:
        acessorio = Acessorio(entrada_veiculo=entrada, **dados)
        acessorio.full_clean()
        acessorio.save()

    alterar_status_ordem(
        ordem_servico=ordem_bloqueada,
        novo_status=OrdemServico.Status.AGUARDANDO_ORCAMENTO,
        responsavel=responsavel,
        observacao="Entrada da motocicleta e checklist registrados.",
    )
    return entrada
