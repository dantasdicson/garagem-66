from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from ..serializers import AlterarSenhaSerializer, Garagem66TokenObtainPairSerializer, UsuarioSerializer


class Garagem66TokenObtainPairView(TokenObtainPairView):
    serializer_class = Garagem66TokenObtainPairSerializer


class PerfilAtualView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)


class AlterarSenhaView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = AlterarSenhaSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)
