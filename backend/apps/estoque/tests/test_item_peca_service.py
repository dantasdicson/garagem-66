from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.estoque.models import ItemPeca, Peca
from apps.estoque.services import excluir_item_peca, registrar_item_peca
from apps.oficina.models import Cliente, Motocicleta, Orcamento, OrdemServico
from apps.usuarios.models import Usuario


class ItemPecaServiceTests(TestCase):
    def setUp(self):
        self.atendente = Usuario.objects.create_user(
            username="atendente-item-peca",
            email="atendente-item-peca@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.ATENDENTE,
        )
        cliente = Cliente.objects.create(nome="Cliente de Teste")
        motocicleta = Motocicleta.objects.create(
            cliente=cliente,
            marca="Honda",
            modelo="CB 500X",
            ano=2024,
            placa="ABC1D23",
        )
        self.ordem = OrdemServico.objects.create(
            numero="OS-TESTE-001",
            motocicleta=motocicleta,
            cliente=cliente,
            descricao_problema="Revisão de teste",
            status=OrdemServico.Status.EM_EXECUCAO,
        )
        Orcamento.objects.create(ordem_servico=self.ordem, status=Orcamento.Status.APROVADO)
        self.peca = Peca.objects.create(
            codigo="FLT-001",
            nome="Filtro de óleo",
            quantidade_estoque=5,
            valor_unitario=Decimal("45.90"),
        )

    def test_registrar_item_desconta_estoque(self):
        item = registrar_item_peca(
            ordem_servico=self.ordem,
            responsavel=self.atendente,
            peca=self.peca,
            quantidade=2,
            valor_unitario=Decimal("45.90"),
        )

        self.peca.refresh_from_db()
        self.assertEqual(item.quantidade, 2)
        self.assertEqual(self.peca.quantidade_estoque, 3)

    def test_nao_permite_quantidade_maior_que_estoque(self):
        with self.assertRaises(ValidationError):
            registrar_item_peca(
                ordem_servico=self.ordem,
                responsavel=self.atendente,
                peca=self.peca,
                quantidade=6,
                valor_unitario=Decimal("45.90"),
            )

        self.peca.refresh_from_db()
        self.assertEqual(self.peca.quantidade_estoque, 5)
        self.assertFalse(ItemPeca.objects.exists())

    def test_excluir_item_devolve_quantidade_ao_estoque(self):
        item = registrar_item_peca(
            ordem_servico=self.ordem,
            responsavel=self.atendente,
            peca=self.peca,
            quantidade=2,
            valor_unitario=Decimal("45.90"),
        )

        excluir_item_peca(item=item, responsavel=self.atendente)

        self.peca.refresh_from_db()
        self.assertEqual(self.peca.quantidade_estoque, 5)
        self.assertFalse(ItemPeca.objects.exists())
