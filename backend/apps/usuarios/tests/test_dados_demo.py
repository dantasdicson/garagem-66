from django.core.management import call_command
from django.test import TestCase

from apps.oficina.models import Cliente, Orcamento, OrdemServico
from apps.usuarios.models import Usuario


class DadosDemoCommandTests(TestCase):
    def test_comando_e_idempotente_e_cria_fluxo_pronto(self):
        call_command("criar_dados_demo", verbosity=0)
        call_command("criar_dados_demo", verbosity=0)

        self.assertEqual(Usuario.objects.filter(username__in=(
            "admin.demo", "atendente.demo", "mecanico.demo", "52998224725"
        )).count(), 4)
        self.assertEqual(Cliente.objects.filter(cpf="52998224725").count(), 1)
        ordem = OrdemServico.objects.get(numero="OS-DEMO-001")
        self.assertEqual(ordem.status, OrdemServico.Status.AGUARDANDO_APROVACAO)
        self.assertEqual(Orcamento.objects.filter(ordem_servico=ordem).count(), 1)
        self.assertTrue(Usuario.objects.get(username="admin.demo").check_password("Garagem66@Demo"))
        self.assertFalse(Usuario.objects.get(username="admin.demo").is_staff)
