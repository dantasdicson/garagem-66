from django.contrib import admin

from .models import Acessorio, Avaria, Cliente, EntradaVeiculo, Foto, HistoricoStatusOrdem, ItemChecklistEntrada, ItemOrcamentoPeca, ItemOrcamentoServico, ItemServico, ModeloMotocicleta, Motocicleta, Orcamento, OrdemServico

admin.site.register([Cliente, Motocicleta, OrdemServico, ItemServico, EntradaVeiculo, ItemChecklistEntrada, Foto, Avaria, Acessorio])


@admin.register(ModeloMotocicleta)
class ModeloMotocicletaAdmin(admin.ModelAdmin):
    list_display = ("marca", "modelo", "categoria", "ativo")
    list_filter = ("marca", "categoria", "ativo")
    search_fields = ("marca", "modelo")


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ("ordem_servico", "status", "valor_total", "validade", "criado_em")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ItemOrcamentoSomenteLeituraAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ItemOrcamentoServico, ItemOrcamentoSomenteLeituraAdmin)
admin.site.register(ItemOrcamentoPeca, ItemOrcamentoSomenteLeituraAdmin)
admin.site.register(HistoricoStatusOrdem, ItemOrcamentoSomenteLeituraAdmin)
