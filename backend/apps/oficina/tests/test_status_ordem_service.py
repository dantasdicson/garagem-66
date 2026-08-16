from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.oficina.models import Cliente, HistoricoStatusOrdem, Motocicleta, OrdemServico
from apps.oficina.services import alterar_status_ordem
from apps.usuarios.models import Usuario


class StatusOrdemServiceTests(TestCase):
    def setUp(self):
        self.atendente = Usuario.objects.create_user(
            username="atendente-status",
            email="atendente-status@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.ATENDENTE,
        )
        cliente = Cliente.objects.create(nome="Cliente do histórico")
        motocicleta = Motocicleta.objects.create(
            cliente=cliente, marca="Honda", modelo="NC 750X", ano=2025, placa="HIS1A23"
        )
        self.ordem = OrdemServico.objects.create(
            numero="OS-HIS-001",
            motocicleta=motocicleta,
            cliente=cliente,
            descricao_problema="Revisão",
        )

    def test_alteracao_registra_status_responsavel_data_e_observacao(self):
        alterar_status_ordem(
            ordem_servico=self.ordem,
            novo_status=OrdemServico.Status.AGUARDANDO_ORCAMENTO,
            responsavel=self.atendente,
            observacao="Vistoria concluída.",
        )

        self.ordem.refresh_from_db()
        historico = HistoricoStatusOrdem.objects.get()
        self.assertEqual(self.ordem.status, OrdemServico.Status.AGUARDANDO_ORCAMENTO)
        self.assertEqual(historico.status_anterior, OrdemServico.Status.ABERTA)
        self.assertEqual(historico.novo_status, OrdemServico.Status.AGUARDANDO_ORCAMENTO)
        self.assertEqual(historico.responsavel, self.atendente)
        self.assertEqual(historico.observacao, "Vistoria concluída.")
        self.assertIsNotNone(historico.criado_em)

    def test_nao_registra_transicao_para_o_mesmo_status(self):
        with self.assertRaises(ValidationError):
            alterar_status_ordem(
                ordem_servico=self.ordem,
                novo_status=OrdemServico.Status.ABERTA,
                responsavel=self.atendente,
            )
        self.assertFalse(HistoricoStatusOrdem.objects.exists())
