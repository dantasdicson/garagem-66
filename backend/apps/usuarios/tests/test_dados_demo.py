from django.core.management import call_command
from django.test import TestCase

from apps.estoque.models import RequisicaoPeca
from apps.oficina.models import Cliente, EntradaVeiculo, Motocicleta, Orcamento, OrdemServico
from apps.usuarios.models import Usuario


class DadosDemoCommandTests(TestCase):
    def test_comando_e_idempotente_e_cria_fluxo_pronto(self):
        call_command("criar_dados_demo", verbosity=0)
        call_command("criar_dados_demo", verbosity=0)

        self.assertEqual(Usuario.objects.filter(username__in=(
            "luiz.henrique", "fabio", "danrley", "52998224725"
        )).count(), 4)
        self.assertEqual(Cliente.objects.filter(cpf="52998224725").count(), 1)
        ordem = OrdemServico.objects.get(numero="OS-2026-0066")
        self.assertEqual(ordem.status, OrdemServico.Status.AGUARDANDO_APROVACAO)
        self.assertEqual(Orcamento.objects.filter(ordem_servico=ordem).count(), 1)
        self.assertEqual(EntradaVeiculo.objects.filter(ordem_servico=ordem).count(), 1)
        requisicoes = RequisicaoPeca.objects.filter(ordem_servico__numero="OS-2026-0067")
        self.assertEqual(requisicoes.count(), 6)
        self.assertEqual(requisicoes.filter(status=RequisicaoPeca.Status.PENDENTE).count(), 4)
        self.assertEqual(requisicoes.filter(status=RequisicaoPeca.Status.RECUSADA).count(), 2)
        self.assertTrue(Usuario.objects.get(username="luiz.henrique").check_password("Garagem66@Demo"))
        administrador = Usuario.objects.get(username="luiz.henrique")
        self.assertTrue(administrador.is_staff)
        self.assertTrue(administrador.is_superuser)

        self.assertEqual(Usuario.objects.filter(username__in=(
            "renato.almeida", "camila.rocha", "bruno.martins", "11144477735"
        )).count(), 4)
        self.assertEqual(Cliente.objects.filter(cpf="11144477735", nome="Mariana Costa").count(), 1)
        motocicleta_video = Motocicleta.objects.get(placa="TST6A66")
        self.assertEqual(motocicleta_video.cliente.cpf, "11144477735")
        self.assertEqual(motocicleta_video.modelo, "CRF 1100L Africa Twin")
        self.assertEqual(motocicleta_video.ano, 2024)
        self.assertFalse(OrdemServico.objects.filter(motocicleta=motocicleta_video).exists())
        self.assertTrue(Usuario.objects.get(username="renato.almeida").check_password("Garagem66@Demo"))
        self.assertTrue(Usuario.objects.get(username="renato.almeida").is_superuser)
