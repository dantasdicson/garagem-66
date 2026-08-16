from .acessorio import AcessorioSerializer
from .avaria import AvariaSerializer
from .cliente import ClienteSerializer
from .entrada_veiculo import EntradaVeiculoSerializer
from .foto import FotoSerializer
from .historico_status_ordem import HistoricoStatusOrdemSerializer
from .item_servico import ItemServicoSerializer
from .item_checklist_entrada import ItemChecklistEntradaSerializer
from .item_orcamento_peca import ItemOrcamentoPecaSerializer
from .item_orcamento_servico import ItemOrcamentoServicoSerializer
from .motocicleta import MotocicletaSerializer
from .modelo_motocicleta import ModeloMotocicletaSerializer
from .orcamento import OrcamentoSerializer
from .ordem_servico import AcaoStatusOrdemSerializer, OrdemServicoSerializer, ReabrirOrdemSerializer

__all__ = [
    "AcessorioSerializer", "AvariaSerializer", "ClienteSerializer", "EntradaVeiculoSerializer",
    "FotoSerializer", "HistoricoStatusOrdemSerializer", "ItemChecklistEntradaSerializer", "ItemOrcamentoPecaSerializer",
    "ItemOrcamentoServicoSerializer", "ItemServicoSerializer", "ModeloMotocicletaSerializer", "MotocicletaSerializer", "OrcamentoSerializer",
    "AcaoStatusOrdemSerializer", "OrdemServicoSerializer", "ReabrirOrdemSerializer",
]
