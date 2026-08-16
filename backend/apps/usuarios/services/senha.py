from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction


@transaction.atomic
def alterar_senha(*, usuario, senha_atual, nova_senha):
    if not usuario.check_password(senha_atual):
        raise ValidationError({"senha_atual": "A senha atual está incorreta."})
    validate_password(nova_senha, user=usuario)
    usuario.set_password(nova_senha)
    usuario.deve_alterar_senha = False
    usuario.save(update_fields=("password", "deve_alterar_senha"))
    return usuario
