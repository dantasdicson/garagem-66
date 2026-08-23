from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.estoque.models import Peca
from apps.oficina.models import Cliente, HistoricoStatusOrdem, ItemOrcamentoPeca, ItemOrcamentoServico, ItemServico, Motocicleta, Orcamento, OrdemServico
from apps.oficina.services import adicionar_peca_prevista, adicionar_servico_previsto, decidir_orcamento, emitir_orcamento, remover_item_previsto
from apps.usuarios.models import Usuario


class OrcamentoServiceTests(TestCase):
    def setUp(self):
        self.atendente = Usuario.objects.create_user(
            username="atendente-orcamento",
            email="atendente@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.ATENDENTE,
        )
        self.cliente_usuario = Usuario.objects.create_user(
            username="cliente-orcamento",
            email="cliente@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.CLIENTE,
        )
        self.outro_cliente = Usuario.objects.create_user(
            username="outro-cliente",
            email="outro-cliente@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.CLIENTE,
        )
        cliente = Cliente.objects.create(nome="Cliente do orçamento", usuario=self.cliente_usuario)
        motocicleta = Motocicleta.objects.create(
            cliente=cliente,
            marca="Triumph",
            modelo="Tiger 900",
            ano=2025,
            placa="ORC1A23",
        )
        self.ordem = OrdemServico.objects.create(
            numero="OS-ORC-001",
            motocicleta=motocicleta,
            cliente=cliente,
            descricao_problema="Manutenção corretiva",
            status=OrdemServico.Status.AGUARDANDO_ORCAMENTO,
        )

    def emitir(self):
        return emitir_orcamento(
            ordem_servico=self.ordem,
            emitido_por=self.atendente,
            valor_mao_obra=Decimal("300.00"),
            valor_pecas=Decimal("450.00"),
        )

    def test_emitir_orcamento_atualiza_ordem(self):
        orcamento = self.emitir()

        self.ordem.refresh_from_db()
        self.assertEqual(orcamento.status, Orcamento.Status.AGUARDANDO_APROVACAO)
        self.assertEqual(orcamento.emitido_por, self.atendente)
        self.assertEqual(orcamento.validade, timezone.localdate() + timedelta(days=7))
        self.assertEqual(self.ordem.status, OrdemServico.Status.AGUARDANDO_APROVACAO)
        historico = HistoricoStatusOrdem.objects.get(ordem_servico=self.ordem)
        self.assertEqual(historico.responsavel, self.atendente)
        self.assertEqual(historico.novo_status, OrdemServico.Status.AGUARDANDO_APROVACAO)

    def test_nao_emite_orcamento_sem_valor(self):
        with self.assertRaisesMessage(ValidationError, "Informe um valor total maior que zero"):
            emitir_orcamento(
                ordem_servico=self.ordem,
                emitido_por=self.atendente,
                valor_mao_obra=Decimal("0"),
                valor_pecas=Decimal("0"),
            )

        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.status, OrdemServico.Status.AGUARDANDO_ORCAMENTO)
        self.assertFalse(Orcamento.objects.exists())

    def test_cliente_proprietario_pode_aprovar(self):
        orcamento = self.emitir()

        decidir_orcamento(
            orcamento=orcamento,
            cliente_usuario=self.cliente_usuario,
            novo_status=Orcamento.Status.APROVADO,
        )

        orcamento.refresh_from_db()
        self.ordem.refresh_from_db()
        self.assertEqual(orcamento.status, Orcamento.Status.APROVADO)
        self.assertEqual(orcamento.decidido_por, self.cliente_usuario)
        self.assertEqual(self.ordem.status, OrdemServico.Status.EM_EXECUCAO)
        self.assertEqual(HistoricoStatusOrdem.objects.filter(ordem_servico=self.ordem).count(), 2)

    def test_recusa_conclui_ordem_como_nao_aprovada(self):
        orcamento = self.emitir()

        decidir_orcamento(
            orcamento=orcamento,
            cliente_usuario=self.cliente_usuario,
            novo_status=Orcamento.Status.RECUSADO,
        )

        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.status, OrdemServico.Status.CONCLUIDA_NAO_APROVADA)
        self.assertIsNotNone(self.ordem.concluida_em)

    def test_outro_cliente_nao_pode_decidir(self):
        orcamento = self.emitir()

        with self.assertRaises(ValidationError):
            decidir_orcamento(
                orcamento=orcamento,
                cliente_usuario=self.outro_cliente,
                novo_status=Orcamento.Status.APROVADO,
            )

    def test_orcamento_nao_pode_ser_decidido_duas_vezes(self):
        orcamento = self.emitir()
        decidir_orcamento(
            orcamento=orcamento,
            cliente_usuario=self.cliente_usuario,
            novo_status=Orcamento.Status.APROVADO,
        )

        with self.assertRaises(ValidationError):
            decidir_orcamento(
                orcamento=orcamento,
                cliente_usuario=self.cliente_usuario,
                novo_status=Orcamento.Status.RECUSADO,
            )

    def test_itens_previstos_calculam_totais_sem_registrar_execucao(self):
        orcamento = self.emitir()
        peca = Peca.objects.create(
            codigo="ORC-PEC-001",
            nome="Pastilha de freio",
            quantidade_estoque=4,
            valor_unitario=Decimal("150.00"),
        )

        adicionar_servico_previsto(
            orcamento=orcamento,
            responsavel=self.atendente,
            descricao="Troca das pastilhas",
            quantidade=1,
            valor_unitario=Decimal("200.00"),
        )
        adicionar_peca_prevista(
            orcamento=orcamento,
            responsavel=self.atendente,
            peca=peca,
            quantidade=2,
            valor_unitario=Decimal("150.00"),
        )

        orcamento.refresh_from_db()
        peca.refresh_from_db()
        self.assertEqual(orcamento.valor_mao_obra, Decimal("200.00"))
        self.assertEqual(orcamento.valor_pecas, Decimal("300.00"))
        self.assertEqual(orcamento.valor_total, Decimal("500.00"))
        self.assertEqual(peca.quantidade_estoque, 4)
        self.assertFalse(ItemServico.objects.exists())

    def test_orcamento_decidido_nao_aceita_novos_itens(self):
        orcamento = self.emitir()
        decidir_orcamento(
            orcamento=orcamento,
            cliente_usuario=self.cliente_usuario,
            novo_status=Orcamento.Status.APROVADO,
        )

        with self.assertRaises(ValidationError):
            adicionar_servico_previsto(
                orcamento=orcamento,
                responsavel=self.atendente,
                descricao="Serviço tardio",
                quantidade=1,
                valor_unitario=Decimal("100.00"),
            )

    def test_remover_item_previsto_recalcula_total(self):
        orcamento = self.emitir()
        primeiro = adicionar_servico_previsto(
            orcamento=orcamento,
            responsavel=self.atendente,
            descricao="Primeiro serviço",
            quantidade=1,
            valor_unitario=Decimal("100.00"),
        )
        adicionar_servico_previsto(
            orcamento=orcamento,
            responsavel=self.atendente,
            descricao="Segundo serviço",
            quantidade=1,
            valor_unitario=Decimal("250.00"),
        )

        remover_item_previsto(item=primeiro, responsavel=self.atendente)

        orcamento.refresh_from_db()
        self.assertEqual(orcamento.valor_mao_obra, Decimal("250.00"))
        self.assertEqual(ItemOrcamentoServico.objects.count(), 1)
        self.assertFalse(ItemOrcamentoPeca.objects.exists())
