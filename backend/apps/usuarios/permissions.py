from rest_framework.permissions import BasePermission

from .models import Usuario


def _acesso_liberado(usuario):
    return bool(usuario.is_authenticated and not usuario.deve_alterar_senha)


class IsAdministrador(BasePermission):
    message = "Esta ação exige o perfil de administrador."

    def has_permission(self, request, view):
        return bool(
            _acesso_liberado(request.user)
            and request.user.tipo == Usuario.Tipo.ADMINISTRADOR
        )


class IsEquipeOficina(BasePermission):
    message = "Esta ação exige um perfil da equipe da oficina."

    def has_permission(self, request, view):
        return bool(
            _acesso_liberado(request.user)
            and request.user.tipo in {
                Usuario.Tipo.ADMINISTRADOR,
                Usuario.Tipo.ATENDENTE,
                Usuario.Tipo.MECANICO,
            }
        )


class PodeGerenciarOperacao(BasePermission):
    message = "Esta ação exige o perfil de administrador ou atendente."

    def has_permission(self, request, view):
        return bool(
            _acesso_liberado(request.user)
            and request.user.tipo in {
                Usuario.Tipo.ADMINISTRADOR,
                Usuario.Tipo.ATENDENTE,
            }
        )


class IsMecanico(BasePermission):
    message = "Esta ação exige o perfil de mecânico."

    def has_permission(self, request, view):
        return bool(
            _acesso_liberado(request.user)
            and request.user.tipo == Usuario.Tipo.MECANICO
        )


class IsCliente(BasePermission):
    message = "Esta ação exige o perfil de cliente."

    def has_permission(self, request, view):
        return bool(
            _acesso_liberado(request.user)
            and request.user.tipo == Usuario.Tipo.CLIENTE
        )


class SenhaAtualizada(BasePermission):
    message = "Altere a senha inicial antes de continuar."

    def has_permission(self, request, view):
        return _acesso_liberado(request.user)
