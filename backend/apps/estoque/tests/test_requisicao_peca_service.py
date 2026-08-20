from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.estoque.models import Peca, RequisicaoPeca
from apps.estoque.services import criar_requisicao_peca, decidir_requisicao_peca
from apps.oficina.models import Cliente, Motocicleta, OrdemServico
from apps.usuarios.models import Usuario


class RequisicaoPecaServiceTests(TestCase):
    def setUp(self):
        self.administrador = Usuario.objects.create_user(
            username="admin",
            email="admin@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.ADMINISTRADOR,
        )
        self.mecanico = Usuario.objects.create_user(
            username="mecanico",
            email="mecanico@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.MECANICO,
        )
        self.outro_mecanico = Usuario.objects.create_user(
            username="outro-mecanico",
            email="outro@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.MECANICO,
        )
        cliente = Cliente.objects.create(nome="Cliente de Teste")
        motocicleta = Motocicleta.objects.create(
            cliente=cliente,
            marca="Yamaha",
            modelo="Ténéré 700",
            ano=2025,
            placa="REQ1A23",
        )
        self.ordem = OrdemServico.objects.create(
            numero="OS-REQ-001",
            motocicleta=motocicleta,
            cliente=cliente,
            mecanico=self.mecanico,
            descricao_problema="Revisão geral",
        )
        self.peca = Peca.objects.create(
            codigo="REQ-001",
            nome="Kit de relação",
            quantidade_estoque=3,
        )

    def criar_requisicao(self):
        return criar_requisicao_peca(
            ordem_servico=self.ordem,
            mecanico=self.mecanico,
            peca=self.peca,
            quantidade=1,
            observacoes="Necessária para concluir o serviço.",
        )

    def test_mecanico_atribuido_pode_criar_requisicao(self):
        requisicao = self.criar_requisicao()

        self.assertEqual(requisicao.status, RequisicaoPeca.Status.PENDENTE)
        self.assertEqual(requisicao.mecanico, self.mecanico)
        self.assertEqual(requisicao.peca, self.peca)

    def test_outro_mecanico_nao_pode_criar_requisicao(self):
        with self.assertRaises(ValidationError):
            criar_requisicao_peca(
                ordem_servico=self.ordem,
                mecanico=self.outro_mecanico,
                peca=self.peca,
                quantidade=1,
            )

    def test_administrador_pode_aprovar_requisicao(self):
        requisicao = self.criar_requisicao()

        requisicao = decidir_requisicao_peca(
            requisicao=requisicao,
            administrador=self.administrador,
            novo_status=RequisicaoPeca.Status.APROVADA,
        )

        self.assertEqual(requisicao.status, RequisicaoPeca.Status.APROVADA)
        self.assertEqual(requisicao.decidida_por, self.administrador)
        self.assertIsNotNone(requisicao.decidida_em)
        self.peca.refresh_from_db()
        self.assertEqual(self.peca.quantidade_estoque, 2)
        self.assertEqual(requisicao.itens.count(), 1)

    def test_aprovacao_sem_estoque_e_impedida(self):
        requisicao = self.criar_requisicao()
        self.peca.quantidade_estoque = 0
        self.peca.save(update_fields=("quantidade_estoque",))

        with self.assertRaises(ValidationError):
            decidir_requisicao_peca(
                requisicao=requisicao,
                administrador=self.administrador,
                novo_status=RequisicaoPeca.Status.APROVADA,
            )

        requisicao.refresh_from_db()
        self.assertEqual(requisicao.status, RequisicaoPeca.Status.PENDENTE)
        self.assertFalse(requisicao.itens.exists())

    def test_mecanico_nao_pode_aprovar_requisicao(self):
        requisicao = self.criar_requisicao()

        with self.assertRaises(ValidationError):
            decidir_requisicao_peca(
                requisicao=requisicao,
                administrador=self.mecanico,
                novo_status=RequisicaoPeca.Status.APROVADA,
            )

        requisicao.refresh_from_db()
        self.peca.refresh_from_db()
        self.assertEqual(requisicao.status, RequisicaoPeca.Status.PENDENTE)
        self.assertEqual(self.peca.quantidade_estoque, 3)

    def test_requisicao_nao_pode_ser_decidida_duas_vezes(self):
        requisicao = self.criar_requisicao()
        decidir_requisicao_peca(
            requisicao=requisicao,
            administrador=self.administrador,
            novo_status=RequisicaoPeca.Status.RECUSADA,
        )

        with self.assertRaises(ValidationError):
            decidir_requisicao_peca(
                requisicao=requisicao,
                administrador=self.administrador,
                novo_status=RequisicaoPeca.Status.APROVADA,
            )
