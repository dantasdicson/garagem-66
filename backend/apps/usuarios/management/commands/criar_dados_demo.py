import os
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.estoque.models import Peca
from apps.oficina.models import (
    Cliente,
    HistoricoStatusOrdem,
    ItemOrcamentoPeca,
    ItemOrcamentoServico,
    ModeloMotocicleta,
    Motocicleta,
    Orcamento,
    OrdemServico,
)
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = "Cria ou restaura as contas e os dados fictícios usados na apresentação."

    @transaction.atomic
    def handle(self, *args, **options):
        senha = os.environ.get("DEMO_PASSWORD", "Garagem66@Demo")
        fontes = {
            "Honda": "https://www.honda.com.br/motos/adventure",
            "Yamaha": "https://www.yamaha-motor.com.br/trail",
            "BMW": "https://www.bmw-motorrad.com.br/pt/models/modeloverview.html",
            "Triumph": "https://www.triumphmotorcycles.com.br/motocicletas/adventure",
            "Suzuki": "https://suzukimotos.com.br/",
            "Royal Enfield": "https://www.royalenfield.com/br/pt/motorcycles/new-himalayan/",
        }
        catalogo = {
            "Honda": {
                "TRAIL": ["NXR 160 Bros", "XRE 190", "XR 300L Tornado", "XRE 300 Sahara"],
                "BIG_TRAIL": ["NX 500", "NC 750X", "XL 750 Transalp", "CRF 1100L Africa Twin"],
            },
            "Yamaha": {
                "TRAIL": ["Crosser 150 S ABS", "Crosser 150 Z ABS", "Lander Connected"],
                "BIG_TRAIL": ["Ténéré 700"],
            },
            "BMW": {
                "TRAIL": ["G 310 GS"],
                "BIG_TRAIL": ["F 800 GS", "F 900 GS", "F 900 GS Adventure", "R 1300 GS", "R 1300 GS Adventure"],
            },
            "Triumph": {
                "TRAIL": [],
                "BIG_TRAIL": ["Tiger Sport 660", "Tiger Sport 800", "Tiger 900", "Tiger 1200"],
            },
            "Suzuki": {
                "TRAIL": [],
                "BIG_TRAIL": ["V-Strom 800 DE", "V-Strom 1050"],
            },
            "Royal Enfield": {
                "TRAIL": ["Himalayan 450"],
                "BIG_TRAIL": [],
            },
        }
        for marca, categorias in catalogo.items():
            for categoria, modelos in categorias.items():
                for modelo in modelos:
                    ModeloMotocicleta.objects.update_or_create(
                        marca=marca,
                        modelo=modelo,
                        defaults={"categoria": categoria, "ativo": True, "fonte_url": fontes[marca]},
                    )
        usuarios = {}
        configuracoes = {
            "admin.demo": ("Administrador", "Demo", Usuario.Tipo.ADMINISTRADOR),
            "atendente.demo": ("Atendente", "Demo", Usuario.Tipo.ATENDENTE),
            "mecanico.demo": ("Mecânico", "Demo", Usuario.Tipo.MECANICO),
            "52998224725": ("Marina", "Oliveira", Usuario.Tipo.CLIENTE),
        }
        for username, (nome, sobrenome, tipo) in configuracoes.items():
            eh_administrador = tipo == Usuario.Tipo.ADMINISTRADOR
            usuario, _ = Usuario.objects.update_or_create(
                username=username,
                defaults={
                    "email": f"{username.replace('.', '-')}@demo.garagem66.local",
                    "first_name": nome,
                    "last_name": sobrenome,
                    "tipo": tipo,
                    "is_active": True,
                    "is_staff": eh_administrador,
                    "is_superuser": eh_administrador,
                    "deve_alterar_senha": False,
                },
            )
            usuario.set_password(senha)
            usuario.save(update_fields=("password",))
            usuarios[tipo] = usuario

        cliente, _ = Cliente.objects.update_or_create(
            cpf="52998224725",
            defaults={
                "usuario": usuarios[Usuario.Tipo.CLIENTE],
                "nome": "Marina Oliveira",
                "data_nascimento": date(1990, 2, 1),
                "email": "52998224725@demo.garagem66.local",
                "telefone": "(11) 99999-0066",
                "endereco": "Rua da Motocicleta, 66 - São Paulo/SP",
            },
        )
        motocicleta, _ = Motocicleta.objects.update_or_create(
            placa="GDM6A66",
            defaults={
                "cliente": cliente,
                "marca": "Honda",
                "modelo": "CB 500X",
                "ano": 2024,
                "chassi": "9C2DEMO6600000001",
                "cor": "Vermelha",
            },
        )
        peca, _ = Peca.objects.update_or_create(
            codigo="DEMO-FLT-001",
            defaults={
                "nome": "Filtro de óleo",
                "descricao": "Peça fictícia para demonstração.",
                "quantidade_estoque": 12,
                "quantidade_minima": 3,
                "valor_unitario": Decimal("44.90"),
            },
        )
        ordem, _ = OrdemServico.objects.update_or_create(
            numero="OS-DEMO-001",
            defaults={
                "motocicleta": motocicleta,
                "cliente": cliente,
                "mecanico": usuarios[Usuario.Tipo.MECANICO],
                "tipo_manutencao": OrdemServico.TipoManutencao.PREVENTIVA,
                "descricao_problema": "Revisão preventiva para apresentação do sistema.",
                "status": OrdemServico.Status.AGUARDANDO_APROVACAO,
                "concluida_em": None,
            },
        )
        orcamento, _ = Orcamento.objects.update_or_create(
            ordem_servico=ordem,
            defaults={
                "emitido_por": usuarios[Usuario.Tipo.ATENDENTE],
                "status": Orcamento.Status.AGUARDANDO_APROVACAO,
                "valor_mao_obra": Decimal("280.00"),
                "valor_pecas": Decimal("89.80"),
                "observacoes": "Orçamento fictício pronto para aprovação do cliente.",
                "validade": timezone.localdate() + timedelta(days=30),
                "decidido_em": None,
                "decidido_por": None,
            },
        )
        ItemOrcamentoServico.objects.update_or_create(
            orcamento=orcamento,
            descricao="Revisão preventiva completa",
            defaults={"quantidade": 1, "valor_unitario": Decimal("280.00")},
        )
        ItemOrcamentoPeca.objects.update_or_create(
            orcamento=orcamento,
            peca=peca,
            defaults={"quantidade": 2, "valor_unitario": Decimal("44.90")},
        )
        HistoricoStatusOrdem.objects.get_or_create(
            ordem_servico=ordem,
            status_anterior=OrdemServico.Status.AGUARDANDO_ORCAMENTO,
            novo_status=OrdemServico.Status.AGUARDANDO_APROVACAO,
            defaults={
                "responsavel": usuarios[Usuario.Tipo.ATENDENTE],
                "observacao": "Orçamento demonstrativo emitido.",
            },
        )
        self.stdout.write(self.style.SUCCESS("Dados de demonstração criados/restaurados com sucesso."))
