from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from ..models import OrdemServico
from ..serializers import AbrirAtendimentoSerializer, AcaoStatusOrdemSerializer, OrdemServicoSerializer, ReabrirOrdemSerializer
from ..services import concluir_ordem, colocar_ordem_aguardando_pecas, reabrir_ordem, retomar_execucao_ordem
from apps.usuarios.models import Usuario
from apps.usuarios.permissions import IsAdministrador, IsEquipeOficina, PodeGerenciarOperacao, SenhaAtualizada

class OrdemServicoViewSet(ModelViewSet):
    queryset = OrdemServico.objects.select_related("cliente", "motocicleta").all()
    serializer_class = OrdemServicoSerializer

    def get_permissions(self):
        if self.action == "reabrir":
            return [IsAdministrador()]
        if self.action in {"aguardar_pecas", "retomar_execucao", "concluir"}:
            return [IsEquipeOficina()]
        return [(PodeGerenciarOperacao if self.request.method not in ("GET", "HEAD", "OPTIONS") else SenhaAtualizada)()]

    @action(detail=False, methods=("post",), url_path="abrir-atendimento")
    def abrir_atendimento(self, request):
        entrada = AbrirAtendimentoSerializer(data=request.data, context={"request": request})
        entrada.is_valid(raise_exception=True)
        ordem = entrada.save()
        return Response(self.get_serializer(ordem).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.tipo == Usuario.Tipo.MECANICO:
            return queryset.filter(mecanico=self.request.user)
        if self.request.user.tipo == Usuario.Tipo.CLIENTE:
            return queryset.filter(cliente__usuario=self.request.user)
        return queryset

    def _executar_acao(self, request, servico, serializer_class=AcaoStatusOrdemSerializer):
        entrada = serializer_class(data=request.data)
        entrada.is_valid(raise_exception=True)
        try:
            ordem = servico(
                ordem_servico=self.get_object(),
                responsavel=request.user,
                observacao=entrada.validated_data["observacao"],
            )
        except DjangoValidationError as erro:
            detalhes = erro.message_dict if hasattr(erro, "message_dict") else erro.messages
            raise serializers.ValidationError(detalhes) from erro
        return Response(self.get_serializer(ordem).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=("post",))
    def aguardar_pecas(self, request, pk=None):
        return self._executar_acao(request, colocar_ordem_aguardando_pecas)

    @action(detail=True, methods=("post",))
    def retomar_execucao(self, request, pk=None):
        return self._executar_acao(request, retomar_execucao_ordem)

    @action(detail=True, methods=("post",))
    def concluir(self, request, pk=None):
        return self._executar_acao(request, concluir_ordem)

    @action(detail=True, methods=("post",))
    def reabrir(self, request, pk=None):
        return self._executar_acao(request, reabrir_ordem, ReabrirOrdemSerializer)
