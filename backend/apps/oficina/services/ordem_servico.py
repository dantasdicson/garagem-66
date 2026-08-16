from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from ..models import Motocicleta, OrdemServico
from .entrada_veiculo import registrar_entrada_veiculo


@transaction.atomic
def abrir_ordem_servico(**dados):
    """Cria a OS e deriva seu número do identificador gerado pelo banco."""
    numero_temporario = f"TMP-{uuid4().hex[:16]}"
    ordem = OrdemServico.objects.create(numero=numero_temporario, **dados)
    numero = f"OS-{timezone.localdate().year}-{ordem.pk:06d}"
    OrdemServico.objects.filter(pk=ordem.pk).update(numero=numero)
    ordem.numero = numero
    return ordem


@transaction.atomic
def abrir_atendimento_com_motocicleta(*, cliente, dados_motocicleta, dados_ordem):
    motocicleta = Motocicleta.objects.create(cliente=cliente, **dados_motocicleta)
    return abrir_ordem_servico(cliente=cliente, motocicleta=motocicleta, **dados_ordem)


@transaction.atomic
def iniciar_atendimento(*, cliente, responsavel, motocicleta=None, dados_motocicleta=None, dados_ordem, dados_entrada):
    if motocicleta is None:
        motocicleta = Motocicleta.objects.create(cliente=cliente, **dados_motocicleta)
    elif motocicleta.cliente_id != cliente.id:
        raise ValueError("A motocicleta não pertence ao cliente informado.")
    ordem = abrir_ordem_servico(cliente=cliente, motocicleta=motocicleta, **dados_ordem)
    entrada = registrar_entrada_veiculo(ordem_servico=ordem, responsavel=responsavel, **dados_entrada)
    return ordem, entrada
