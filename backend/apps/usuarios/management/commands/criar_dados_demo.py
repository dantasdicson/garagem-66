import os
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.estoque.models import Peca, RequisicaoPeca
from apps.oficina.models import (
    Acessorio,
    Avaria,
    Cliente,
    EntradaVeiculo,
    HistoricoStatusOrdem,
    ItemChecklistEntrada,
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
        migracoes_login = {
            "admin.demo": "luiz.henrique",
            "atendente.demo": "fabio",
            "mecanico.demo": "danrley",
        }
        for login_antigo, login_novo in migracoes_login.items():
            Usuario.objects.filter(username=login_antigo).exclude(username=login_novo).update(username=login_novo)

        configuracoes = {
            "luiz.henrique": ("Luiz", "Henrique", Usuario.Tipo.ADMINISTRADOR),
            "fabio": ("Fabio", "Almeida", Usuario.Tipo.ATENDENTE),
            "danrley": ("Danrley", "Santos", Usuario.Tipo.MECANICO),
            "52998224725": ("Danilo", "Jota", Usuario.Tipo.CLIENTE),
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
                "nome": "Danilo Jota",
                "data_nascimento": date(1990, 2, 1),
                "email": "52998224725@demo.garagem66.local",
                "telefone": "(84) 99966-0066",
                "endereco": "Rua das Dunas, 66 - Natal/RN",
            },
        )
        motocicleta, _ = Motocicleta.objects.update_or_create(
            placa="GDM6A66",
            defaults={
                "cliente": cliente,
                "marca": "Honda",
                "modelo": "NX 500",
                "ano": 2024,
                "chassi": "9C2DEMO6600000001",
                "cor": "Preta",
            },
        )
        catalogo_estoque = {
            "DEMO-FLT-001": ("Filtro de óleo", "Filtro para revisão preventiva.", 12, 3, "44.90"),
            "DEMO-OLE-010": ("Óleo 10W40", "Óleo semissintético para motocicletas.", 18, 8, "39.90"),
            "DEMO-PST-020": ("Pastilha de freio dianteira", "Jogo de pastilhas para freio dianteiro.", 6, 4, "129.90"),
            "DEMO-CAB-030": ("Cabo de embreagem", "Cabo de reposição reforçado.", 2, 3, "58.00"),
            "DEMO-KIT-040": ("Kit de relação", "Coroa, corrente e pinhão.", 4, 2, "389.00"),
            "DEMO-PNE-050": ("Pneu traseiro 160/60", "Pneu traseiro sport touring.", 0, 2, "749.00"),
        }
        pecas = {}
        for codigo, (nome, descricao, quantidade, minima, valor) in catalogo_estoque.items():
            peca_item, criada = Peca.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nome": nome,
                    "descricao": descricao,
                    "quantidade_estoque": quantidade,
                    "quantidade_minima": minima,
                    "valor_unitario": Decimal(valor),
                },
            )
            if not criada:
                peca_item.nome = nome
                peca_item.descricao = descricao
                peca_item.quantidade_minima = minima
                peca_item.valor_unitario = Decimal(valor)
                peca_item.save(update_fields=("nome", "descricao", "quantidade_minima", "valor_unitario"))
            pecas[codigo] = peca_item
        peca = pecas["DEMO-FLT-001"]
        ordem, _ = OrdemServico.objects.update_or_create(
            numero="OS-2026-0066",
            defaults={
                "motocicleta": motocicleta,
                "cliente": cliente,
                "mecanico": usuarios[Usuario.Tipo.MECANICO],
                "tipo_manutencao": OrdemServico.TipoManutencao.PREVENTIVA,
                "descricao_problema": "Revisão de 12.000 km, troca de óleo e inspeção do sistema de freios.",
                "status": OrdemServico.Status.AGUARDANDO_APROVACAO,
                "concluida_em": None,
            },
        )
        entrada, _ = EntradaVeiculo.objects.update_or_create(
            ordem_servico=ordem,
            defaults={
                "quilometragem": 12184,
                "nivel_combustivel": "1/2 - Médio (50%)",
                "motivo_entrada": "Revisão periódica de 12.000 km.",
                "observacoes": "Motocicleta recebida por Fabio e encaminhada ao mecânico Danrley.",
            },
        )
        itens_pneu = {
            ItemChecklistEntrada.Item.PNEU_DIANTEIRO,
            ItemChecklistEntrada.Item.PNEU_TRASEIRO,
        }
        for item in ItemChecklistEntrada.Item.values:
            ItemChecklistEntrada.objects.update_or_create(
                entrada_veiculo=entrada,
                item=item,
                defaults={
                    "percentual": 75 if item == ItemChecklistEntrada.Item.PNEU_DIANTEIRO else (
                        70 if item == ItemChecklistEntrada.Item.PNEU_TRASEIRO else None
                    ),
                    "estado": "" if item in itens_pneu else ItemChecklistEntrada.Estado.NORMAL,
                    "observacao": "Verificado no recebimento.",
                },
            )
        Avaria.objects.update_or_create(
            entrada_veiculo=entrada,
            localizacao="Protetor lateral direito",
            defaults={"descricao": "Risco superficial preexistente, registrado na entrada."},
        )
        Acessorio.objects.get_or_create(entrada_veiculo=entrada, descricao="Protetor de motor")

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
        ordem_execucao, _ = OrdemServico.objects.update_or_create(
            numero="OS-2026-0067",
            defaults={
                "motocicleta": motocicleta,
                "cliente": cliente,
                "mecanico": usuarios[Usuario.Tipo.MECANICO],
                "tipo_manutencao": OrdemServico.TipoManutencao.CORRETIVA,
                "descricao_problema": "Ruído no freio dianteiro identificado durante inspeção.",
                "status": OrdemServico.Status.AGUARDANDO_PECAS,
                "concluida_em": None,
            },
        )
        RequisicaoPeca.objects.update_or_create(
            ordem_servico=ordem_execucao,
            mecanico=usuarios[Usuario.Tipo.MECANICO],
            peca=peca,
            defaults={
                "quantidade": 1,
                "status": RequisicaoPeca.Status.PENDENTE,
                "observacoes": "Solicitação de Danrley para continuidade do serviço.",
                "decidida_em": None,
                "decidida_por": None,
            },
        )
        requisicoes_adicionais = [
            (pecas["DEMO-OLE-010"], 3, RequisicaoPeca.Status.PENDENTE, "Óleo necessário para a revisão."),
            (pecas["DEMO-PST-020"], 1, RequisicaoPeca.Status.PENDENTE, "Pastilhas com desgaste acima do limite."),
            (pecas["DEMO-CAB-030"], 1, RequisicaoPeca.Status.PENDENTE, "Cabo apresentando desgaste no terminal."),
            (pecas["DEMO-KIT-040"], 1, RequisicaoPeca.Status.RECUSADA, "Substituição preventiva não autorizada nesta etapa."),
            (pecas["DEMO-PNE-050"], 1, RequisicaoPeca.Status.RECUSADA, "Item sem estoque; compra externa será avaliada."),
        ]
        for peca_requisitada, quantidade, status_requisicao, observacoes in requisicoes_adicionais:
            RequisicaoPeca.objects.update_or_create(
                ordem_servico=ordem_execucao,
                mecanico=usuarios[Usuario.Tipo.MECANICO],
                peca=peca_requisitada,
                defaults={
                    "quantidade": quantidade,
                    "status": status_requisicao,
                    "observacoes": observacoes,
                    "decidida_em": timezone.now() if status_requisicao == RequisicaoPeca.Status.RECUSADA else None,
                    "decidida_por": usuarios[Usuario.Tipo.ADMINISTRADOR] if status_requisicao == RequisicaoPeca.Status.RECUSADA else None,
                },
            )
        self.stdout.write(self.style.SUCCESS("Dados de demonstração criados/restaurados com sucesso."))
