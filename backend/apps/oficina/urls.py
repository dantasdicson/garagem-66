from rest_framework.routers import DefaultRouter

from .views import AcessorioViewSet, AvariaViewSet, ClienteViewSet, EntradaVeiculoViewSet, FotoViewSet, HistoricoStatusOrdemViewSet, ItemChecklistEntradaViewSet, ItemOrcamentoPecaViewSet, ItemOrcamentoServicoViewSet, ItemServicoViewSet, ModeloMotocicletaViewSet, MotocicletaViewSet, OrcamentoViewSet, OrdemServicoViewSet

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="cliente")
router.register("motocicletas", MotocicletaViewSet, basename="motocicleta")
router.register("modelos-motocicleta", ModeloMotocicletaViewSet, basename="modelo-motocicleta")
router.register("ordens-servico", OrdemServicoViewSet, basename="ordem-servico")
router.register("historico-status-ordens", HistoricoStatusOrdemViewSet, basename="historico-status-ordem")
router.register("orcamentos", OrcamentoViewSet, basename="orcamento")
router.register("orcamento-servicos", ItemOrcamentoServicoViewSet, basename="orcamento-servico")
router.register("orcamento-pecas", ItemOrcamentoPecaViewSet, basename="orcamento-peca")
router.register("itens-servico", ItemServicoViewSet, basename="item-servico")
router.register("entradas-veiculo", EntradaVeiculoViewSet, basename="entrada-veiculo")
router.register("checklist-entrada", ItemChecklistEntradaViewSet, basename="checklist-entrada")
router.register("fotos", FotoViewSet, basename="foto")
router.register("avarias", AvariaViewSet, basename="avaria")
router.register("acessorios", AcessorioViewSet, basename="acessorio")
urlpatterns = router.urls
