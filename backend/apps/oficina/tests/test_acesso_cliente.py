from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.oficina.models import (
    Cliente,
    HistoricoStatusOrdem,
    Motocicleta,
    Orcamento,
    OrdemServico,
)
from apps.usuarios.models import Usuario


class AcessoClienteTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="cliente-acesso",
            email="cliente-acesso@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.CLIENTE,
        )
        self.outro_usuario = Usuario.objects.create_user(
            username="outro-cliente-acesso",
            email="outro-cliente-acesso@garagem66.test",
            password="teste-forte-123",
            tipo=Usuario.Tipo.CLIENTE,
        )
        self.cliente = Cliente.objects.create(nome="Cliente autenticado", usuario=self.usuario)
        self.outro_cliente = Cliente.objects.create(nome="Outro cliente", usuario=self.outro_usuario)
        self.motocicleta = Motocicleta.objects.create(
            cliente=self.cliente, marca="Honda", modelo="CB 500F", ano=2025, placa="ACL1A23"
        )
        self.outra_motocicleta = Motocicleta.objects.create(
            cliente=self.outro_cliente, marca="Yamaha", modelo="MT-03", ano=2025, placa="ACL2B34"
        )
        self.ordem = OrdemServico.objects.create(
            numero="OS-ACL-001",
            motocicleta=self.motocicleta,
            cliente=self.cliente,
            descricao_problema="Revisão",
            status=OrdemServico.Status.AGUARDANDO_APROVACAO,
        )
        self.outra_ordem = OrdemServico.objects.create(
            numero="OS-ACL-002",
            motocicleta=self.outra_motocicleta,
            cliente=self.outro_cliente,
            descricao_problema="Troca de óleo",
            status=OrdemServico.Status.AGUARDANDO_APROVACAO,
        )
        self.orcamento = Orcamento.objects.create(ordem_servico=self.ordem)
        self.outro_orcamento = Orcamento.objects.create(ordem_servico=self.outra_ordem)
        self.historico = HistoricoStatusOrdem.objects.create(
            ordem_servico=self.ordem,
            status_anterior=OrdemServico.Status.AGUARDANDO_ORCAMENTO,
            novo_status=OrdemServico.Status.AGUARDANDO_APROVACAO,
            observacao="Orçamento emitido.",
        )
        self.outro_historico = HistoricoStatusOrdem.objects.create(
            ordem_servico=self.outra_ordem,
            status_anterior=OrdemServico.Status.AGUARDANDO_ORCAMENTO,
            novo_status=OrdemServico.Status.AGUARDANDO_APROVACAO,
            observacao="Outro orçamento emitido.",
        )
        self.api = APIClient()
        self.api.force_authenticate(self.usuario)

    def _ids(self, nome_rota):
        resposta = self.api.get(reverse(nome_rota))
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        dados = resposta.data.get("results", resposta.data) if isinstance(resposta.data, dict) else resposta.data
        return {item["id"] for item in dados}

    def test_cliente_visualiza_somente_o_proprio_cadastro(self):
        self.assertEqual(self._ids("cliente-list"), {self.cliente.id})
        resposta = self.api.get(reverse("cliente-detail", args=(self.outro_cliente.id,)))
        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_cliente_visualiza_somente_as_proprias_motocicletas(self):
        self.assertEqual(self._ids("motocicleta-list"), {self.motocicleta.id})
        resposta = self.api.get(reverse("motocicleta-detail", args=(self.outra_motocicleta.id,)))
        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_cliente_visualiza_somente_as_proprias_ordens(self):
        self.assertEqual(self._ids("ordem-servico-list"), {self.ordem.id})
        resposta = self.api.get(reverse("ordem-servico-detail", args=(self.outra_ordem.id,)))
        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_cliente_visualiza_somente_os_proprios_orcamentos(self):
        self.assertEqual(self._ids("orcamento-list"), {self.orcamento.id})
        resposta = self.api.get(reverse("orcamento-detail", args=(self.outro_orcamento.id,)))
        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_cliente_visualiza_somente_o_historico_das_proprias_ordens(self):
        self.assertEqual(self._ids("historico-status-ordem-list"), {self.historico.id})
        resposta = self.api.get(reverse("historico-status-ordem-detail", args=(self.outro_historico.id,)))
        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_cliente_nao_pode_alterar_dados_operacionais(self):
        resposta = self.api.patch(
            reverse("motocicleta-detail", args=(self.motocicleta.id,)),
            {"cor": "Preta"},
            format="json",
        )
        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)
