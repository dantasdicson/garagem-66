from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.oficina.models import Cliente, ItemServico, Motocicleta, Orcamento, OrdemServico
from apps.oficina.services import registrar_item_servico
from apps.usuarios.models import Usuario


class ExecucaoOrdemServiceTests(TestCase):
    def setUp(self):
        self.mecanico = Usuario.objects.create_user(
            username="mecanico-execucao",
            email="mecanico-execucao@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.MECANICO,
        )
        self.outro_mecanico = Usuario.objects.create_user(
            username="outro-mecanico-execucao",
            email="outro-mecanico-execucao@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.MECANICO,
        )
        cliente = Cliente.objects.create(nome="Cliente da execução")
        motocicleta = Motocicleta.objects.create(
            cliente=cliente, marca="Yamaha", modelo="MT-07", ano=2025, placa="EXE1A23"
        )
        self.ordem = OrdemServico.objects.create(
            numero="OS-EXE-001",
            motocicleta=motocicleta,
            cliente=cliente,
            mecanico=self.mecanico,
            descricao_problema="Troca do kit de transmissão",
            status=OrdemServico.Status.AGUARDANDO_APROVACAO,
        )
        self.orcamento = Orcamento.objects.create(ordem_servico=self.ordem)

    def registrar(self, responsavel=None):
        return registrar_item_servico(
            ordem_servico=self.ordem,
            responsavel=responsavel or self.mecanico,
            descricao="Troca do kit de transmissão",
            quantidade=1,
            valor_unitario=Decimal("250.00"),
        )

    def test_nao_executa_com_orcamento_pendente(self):
        with self.assertRaises(ValidationError):
            self.registrar()
        self.assertFalse(ItemServico.objects.exists())

    def test_mecanico_atribuido_executa_apos_aprovacao(self):
        self.orcamento.status = Orcamento.Status.APROVADO
        self.orcamento.save(update_fields=("status",))
        self.ordem.status = OrdemServico.Status.EM_EXECUCAO
        self.ordem.save(update_fields=("status", "atualizada_em"))

        item = self.registrar()

        self.assertEqual(item.ordem_servico, self.ordem)
        self.assertEqual(ItemServico.objects.count(), 1)

    def test_mecanico_nao_atribuido_nao_executa(self):
        self.orcamento.status = Orcamento.Status.APROVADO
        self.orcamento.save(update_fields=("status",))
        self.ordem.status = OrdemServico.Status.EM_EXECUCAO
        self.ordem.save(update_fields=("status", "atualizada_em"))

        with self.assertRaises(ValidationError):
            self.registrar(responsavel=self.outro_mecanico)
        self.assertFalse(ItemServico.objects.exists())
