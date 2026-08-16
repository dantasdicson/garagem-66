from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.oficina.models import Cliente, EntradaVeiculo, ItemChecklistEntrada, Motocicleta, OrdemServico
from apps.oficina.services import registrar_entrada_veiculo
from apps.usuarios.models import Usuario


class EntradaVeiculoServiceTests(TestCase):
    def setUp(self):
        self.atendente = Usuario.objects.create_user(
            username="atendente-entrada",
            email="atendente-entrada@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.ATENDENTE,
        )
        self.mecanico = Usuario.objects.create_user(
            username="mecanico-entrada",
            email="mecanico-entrada@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.MECANICO,
        )
        cliente = Cliente.objects.create(nome="Cliente da entrada")
        motocicleta = Motocicleta.objects.create(
            cliente=cliente, marca="Honda", modelo="CB 500", ano=2024, placa="ENT1A23"
        )
        self.ordem = OrdemServico.objects.create(
            numero="OS-ENT-001",
            motocicleta=motocicleta,
            cliente=cliente,
            descricao_problema="Revisão geral",
        )
        self.api = APIClient()

    def checklist_completo(self):
        pneus = {
            ItemChecklistEntrada.Item.PNEU_DIANTEIRO,
            ItemChecklistEntrada.Item.PNEU_TRASEIRO,
        }
        return [
            {
                "item": item,
                "percentual": 80 if item in pneus else None,
                "estado": "" if item in pneus else ItemChecklistEntrada.Estado.NORMAL,
            }
            for item in ItemChecklistEntrada.Item.values
        ]

    def test_registra_toda_a_entrada_e_atualiza_ordem(self):
        entrada = registrar_entrada_veiculo(
            ordem_servico=self.ordem,
            responsavel=self.atendente,
            itens_checklist=self.checklist_completo(),
            avarias=[{"descricao": "Risco no tanque", "localizacao": "Lado direito"}],
            acessorios=[{"descricao": "Baú traseiro"}],
            quilometragem=12500,
            nivel_combustivel="Meio tanque",
            motivo_entrada="Revisão de 12 mil km",
        )

        self.ordem.refresh_from_db()
        self.assertEqual(entrada.itens_checklist.count(), len(ItemChecklistEntrada.Item.values))
        self.assertEqual(entrada.avarias.count(), 1)
        self.assertEqual(entrada.acessorios.count(), 1)
        self.assertEqual(self.ordem.status, OrdemServico.Status.AGUARDANDO_ORCAMENTO)

    def test_checklist_incompleto_nao_grava_entrada(self):
        checklist = self.checklist_completo()[:-1]

        with self.assertRaises(ValidationError):
            registrar_entrada_veiculo(
                ordem_servico=self.ordem,
                responsavel=self.atendente,
                itens_checklist=checklist,
                motivo_entrada="Revisão",
            )

        self.assertFalse(EntradaVeiculo.objects.exists())

    def test_erro_em_item_desfaz_toda_a_operacao(self):
        checklist = self.checklist_completo()
        checklist[0]["percentual"] = 101

        with self.assertRaises(ValidationError):
            registrar_entrada_veiculo(
                ordem_servico=self.ordem,
                responsavel=self.atendente,
                itens_checklist=checklist,
                avarias=[{"descricao": "Avaria temporária"}],
                motivo_entrada="Revisão",
            )

        self.ordem.refresh_from_db()
        self.assertFalse(EntradaVeiculo.objects.exists())
        self.assertEqual(self.ordem.status, OrdemServico.Status.ABERTA)

    def test_mecanico_nao_pode_registrar_entrada(self):
        with self.assertRaises(ValidationError):
            registrar_entrada_veiculo(
                ordem_servico=self.ordem,
                responsavel=self.mecanico,
                itens_checklist=self.checklist_completo(),
                motivo_entrada="Revisão",
            )

    def test_endpoint_registra_entrada_aninhada(self):
        self.api.force_authenticate(self.atendente)
        resposta = self.api.post(
            reverse("entrada-veiculo-list"),
            {
                "ordem_servico": self.ordem.pk,
                "quilometragem": 12500,
                "nivel_combustivel": "Meio tanque",
                "motivo_entrada": "Revisão de 12 mil km",
                "observacoes": "Cliente acompanhou a vistoria",
                "itens_checklist": self.checklist_completo(),
                "avarias": [{"descricao": "Risco no tanque", "localizacao": "Lado direito"}],
                "acessorios": [{"descricao": "Baú traseiro"}],
            },
            format="json",
        )

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED, resposta.data)
        self.assertEqual(len(resposta.data["itens_checklist"]), len(ItemChecklistEntrada.Item.values))
        self.assertEqual(len(resposta.data["avarias"]), 1)
        self.assertEqual(len(resposta.data["acessorios"]), 1)
