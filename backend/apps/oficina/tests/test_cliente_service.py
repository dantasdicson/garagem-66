from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.oficina.services import atualizar_cliente, cadastrar_cliente_com_acesso, normalizar_telefone
from apps.usuarios.models import Usuario


class ClienteServiceTests(TestCase):
    def test_cadastro_cria_usuario_com_cpf_e_senha_inicial(self):
        cliente = cadastrar_cliente_com_acesso(
            nome="Maria da Silva",
            cpf="529.982.247-25",
            data_nascimento=date(1990, 2, 1),
            email="maria@garagem66.test",
            telefone="11999999999",
            endereco="Rua de Teste, 66",
        )

        self.assertEqual(cliente.cpf, "52998224725")
        self.assertEqual(cliente.usuario.username, "52998224725")
        self.assertEqual(cliente.usuario.tipo, Usuario.Tipo.CLIENTE)
        self.assertTrue(cliente.usuario.deve_alterar_senha)
        self.assertTrue(cliente.usuario.check_password("01021990"))
        self.assertEqual(cliente.telefone, "(11) 99999-9999")

    def test_cpf_duplicado_e_rejeitado(self):
        dados = {
            "nome": "Maria da Silva",
            "cpf": "52998224725",
            "data_nascimento": date(1990, 2, 1),
            "email": "maria@garagem66.test",
        }
        cadastrar_cliente_com_acesso(**dados)

        dados["email"] = "outra-maria@garagem66.test"
        with self.assertRaises(ValidationError):
            cadastrar_cliente_com_acesso(**dados)

    def test_telefone_aceita_mascara_e_codigo_do_brasil(self):
        self.assertEqual(normalizar_telefone("+55 (11) 99999-8877"), "(11) 99999-8877")
        self.assertEqual(normalizar_telefone("(11) 3333-4455"), "(11) 3333-4455")
        self.assertEqual(normalizar_telefone(""), "")

    def test_telefone_invalido_e_rejeitado(self):
        with self.assertRaises(ValidationError):
            normalizar_telefone("9999-9999")
        with self.assertRaises(ValidationError):
            normalizar_telefone("(11) 89999-9999")

    def test_atualizacao_normaliza_telefone(self):
        cliente = cadastrar_cliente_com_acesso(
            nome="João da Silva",
            cpf="111.444.777-35",
            data_nascimento=date(1985, 5, 10),
            email="joao@garagem66.test",
        )

        atualizar_cliente(
            cliente=cliente,
            nome=cliente.nome,
            email=cliente.email,
            telefone="+55 21 98888-7766",
            endereco="Rua Nova, 10",
        )

        cliente.refresh_from_db()
        self.assertEqual(cliente.telefone, "(21) 98888-7766")
