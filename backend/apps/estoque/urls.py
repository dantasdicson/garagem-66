from rest_framework.routers import DefaultRouter

from .views import ItemPecaViewSet, PecaViewSet, RequisicaoPecaViewSet

router = DefaultRouter()
router.register("pecas", PecaViewSet, basename="peca")
router.register("requisicoes-peca", RequisicaoPecaViewSet, basename="requisicao-peca")
router.register("itens-peca", ItemPecaViewSet, basename="item-peca")
urlpatterns = router.urls
