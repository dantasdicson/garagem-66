from .acessorio import AcessorioViewSet
from .avaria import AvariaViewSet
from .cliente import ClienteViewSet
from .entrada_veiculo import EntradaVeiculoViewSet
from .historico_status_ordem import HistoricoStatusOrdemViewSet
from .foto import FotoViewSet
from .item_servico import ItemServicoViewSet
from .item_checklist_entrada import ItemChecklistEntradaViewSet
from .item_orcamento_peca import ItemOrcamentoPecaViewSet
from .item_orcamento_servico import ItemOrcamentoServicoViewSet
from .motocicleta import MotocicletaViewSet
from .orcamento import OrcamentoViewSet
from .ordem_servico import OrdemServicoViewSet

__all__ = ["AcessorioViewSet", "AvariaViewSet", "ClienteViewSet", "EntradaVeiculoViewSet", "FotoViewSet", "HistoricoStatusOrdemViewSet", "ItemChecklistEntradaViewSet", "ItemOrcamentoPecaViewSet", "ItemOrcamentoServicoViewSet", "ItemServicoViewSet", "MotocicletaViewSet", "OrcamentoViewSet", "OrdemServicoViewSet"]
