from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient

from apps.oficina.services import cadastrar_cliente_com_acesso


class PrimeiroAcessoAPITests(TestCase):
    def setUp(self):
        cadastrar_cliente_com_acesso(
            nome="Cliente Primeiro Acesso",
            cpf="52998224725",
            data_nascimento=date(1990, 2, 1),
            email="primeiro-acesso@garagem66.test",
        )
        self.client = APIClient()

    def autenticar(self):
        resposta = self.client.post(
            "/api/auth/token/",
            {"username": "52998224725", "password": "01021990"},
            format="json",
        )
        self.assertEqual(resposta.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resposta.data['access']}")
        return resposta

    def test_login_informa_necessidade_de_trocar_senha(self):
        resposta = self.autenticar()

        self.assertEqual(resposta.data["usuario"]["tipo"], "CLIENTE")
        self.assertTrue(resposta.data["usuario"]["deve_alterar_senha"])

    def test_cliente_fica_bloqueado_ate_alterar_senha(self):
        self.autenticar()

        bloqueada = self.client.get("/api/oficina/orcamentos/")
        self.assertEqual(bloqueada.status_code, 403)

        alteracao = self.client.post(
            "/api/usuarios/alterar-senha/",
            {"senha_atual": "01021990", "nova_senha": "NovaSenhaForte#2026"},
            format="json",
        )
        self.assertEqual(alteracao.status_code, 200)

        liberada = self.client.get("/api/oficina/orcamentos/")
        self.assertEqual(liberada.status_code, 200)
