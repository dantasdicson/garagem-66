from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.oficina.models import Cliente, HistoricoStatusOrdem, Motocicleta, OrdemServico
from apps.oficina.services import (
    concluir_ordem,
    colocar_ordem_aguardando_pecas,
    reabrir_ordem,
    retomar_execucao_ordem,
)
from apps.usuarios.models import Usuario


class FluxoConclusaoOrdemTests(TestCase):
    def setUp(self):
        self.administrador = Usuario.objects.create_user(
            username="admin-conclusao",
            email="admin-conclusao@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.ADMINISTRADOR,
        )
        self.atendente = Usuario.objects.create_user(
            username="atendente-conclusao",
            email="atendente-conclusao@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.ATENDENTE,
        )
        self.mecanico = Usuario.objects.create_user(
            username="mecanico-conclusao",
            email="mecanico-conclusao@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.MECANICO,
        )
        self.outro_mecanico = Usuario.objects.create_user(
            username="outro-mecanico-conclusao",
            email="outro-mecanico-conclusao@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.MECANICO,
        )
        cliente = Cliente.objects.create(nome="Cliente da conclusão")
        motocicleta = Motocicleta.objects.create(
            cliente=cliente, marca="BMW", modelo="G 310 GS", ano=2025, placa="CON1A23"
        )
        self.ordem = OrdemServico.objects.create(
            numero="OS-CON-001",
            motocicleta=motocicleta,
            cliente=cliente,
            mecanico=self.mecanico,
            descricao_problema="Revisão completa",
            status=OrdemServico.Status.EM_EXECUCAO,
        )
        self.api = APIClient()

    def test_mecanico_atribuido_pode_concluir(self):
        concluir_ordem(ordem_servico=self.ordem, responsavel=self.mecanico, observacao="Revisão finalizada.")

        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.status, OrdemServico.Status.CONCLUIDA)
        self.assertIsNotNone(self.ordem.concluida_em)
        self.assertEqual(self.ordem.historico_status.get().responsavel, self.mecanico)

    def test_mecanico_nao_atribuido_nao_pode_concluir(self):
        with self.assertRaises(ValidationError):
            concluir_ordem(ordem_servico=self.ordem, responsavel=self.outro_mecanico)

    def test_fluxo_aguardar_pecas_e_retomar(self):
        colocar_ordem_aguardando_pecas(ordem_servico=self.ordem, responsavel=self.mecanico)
        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.status, OrdemServico.Status.AGUARDANDO_PECAS)

        retomar_execucao_ordem(ordem_servico=self.ordem, responsavel=self.mecanico)
        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.status, OrdemServico.Status.EM_EXECUCAO)
        self.assertEqual(HistoricoStatusOrdem.objects.filter(ordem_servico=self.ordem).count(), 2)

    def test_apenas_administrador_reabre_ordem_concluida(self):
        concluir_ordem(ordem_servico=self.ordem, responsavel=self.mecanico)

        with self.assertRaises(ValidationError):
            reabrir_ordem(ordem_servico=self.ordem, responsavel=self.atendente, observacao="Retrabalho")

        reabrir_ordem(
            ordem_servico=self.ordem,
            responsavel=self.administrador,
            observacao="Cliente relatou que o problema persistiu.",
        )
        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.status, OrdemServico.Status.EM_EXECUCAO)
        self.assertIsNone(self.ordem.concluida_em)

    def test_reabertura_exige_justificativa(self):
        concluir_ordem(ordem_servico=self.ordem, responsavel=self.mecanico)
        with self.assertRaises(ValidationError):
            reabrir_ordem(ordem_servico=self.ordem, responsavel=self.administrador, observacao="  ")

    def test_nao_conclui_ordem_que_ainda_aguarda_aprovacao(self):
        self.ordem.status = OrdemServico.Status.AGUARDANDO_APROVACAO
        self.ordem.save(update_fields=("status", "atualizada_em"))
        with self.assertRaises(ValidationError):
            concluir_ordem(ordem_servico=self.ordem, responsavel=self.atendente)

    def test_endpoint_de_conclusao_registra_historico(self):
        self.api.force_authenticate(self.mecanico)
        resposta = self.api.post(
            reverse("ordem-servico-concluir", args=(self.ordem.pk,)),
            {"observacao": "Conferência final realizada."},
            format="json",
        )

        self.assertEqual(resposta.status_code, status.HTTP_200_OK, resposta.data)
        self.assertEqual(resposta.data["status"], OrdemServico.Status.CONCLUIDA)
        self.assertTrue(HistoricoStatusOrdem.objects.filter(ordem_servico=self.ordem).exists())
