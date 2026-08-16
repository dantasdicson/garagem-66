import re

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.usuarios.models import Usuario

from ..models import Cliente


def normalizar_cpf(cpf):
    return re.sub(r"\D", "", cpf or "")


def normalizar_telefone(telefone):
    digitos = re.sub(r"\D", "", telefone or "")
    if not digitos:
        return ""
    if digitos.startswith("55") and len(digitos) in {12, 13}:
        digitos = digitos[2:]
    if len(digitos) not in {10, 11}:
        raise ValidationError({"telefone": "Informe um telefone brasileiro com DDD e 10 ou 11 dígitos."})
    if digitos[:2] == "00" or digitos[0] == "0":
        raise ValidationError({"telefone": "Informe um DDD válido, sem o zero inicial."})
    if len(digitos) == 11 and digitos[2] != "9":
        raise ValidationError({"telefone": "Celulares com 11 dígitos devem iniciar com 9 após o DDD."})
    parte_final = f"{digitos[-4:]}"
    parte_inicial = digitos[2:-4]
    return f"({digitos[:2]}) {parte_inicial}-{parte_final}"


def validar_cpf(cpf):
    cpf = normalizar_cpf(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError({"cpf": "Informe um CPF válido com 11 dígitos."})

    for tamanho in (9, 10):
        soma = sum(int(cpf[indice]) * (tamanho + 1 - indice) for indice in range(tamanho))
        digito = (soma * 10) % 11
        digito = 0 if digito == 10 else digito
        if digito != int(cpf[tamanho]):
            raise ValidationError({"cpf": "Informe um CPF válido."})
    return cpf


@transaction.atomic
def cadastrar_cliente_com_acesso(*, nome, cpf, data_nascimento, email, telefone="", endereco=""):
    cpf = validar_cpf(cpf)
    telefone = normalizar_telefone(telefone)
    if Usuario.objects.filter(username=cpf).exists() or Cliente.objects.filter(cpf=cpf).exists():
        raise ValidationError({"cpf": "Já existe um cliente cadastrado com este CPF."})
    if Usuario.objects.filter(email__iexact=email).exists():
        raise ValidationError({"email": "Já existe um usuário cadastrado com este e-mail."})

    partes_nome = nome.strip().split(maxsplit=1)
    usuario = Usuario.objects.create_user(
        username=cpf,
        email=email,
        first_name=partes_nome[0],
        last_name=partes_nome[1] if len(partes_nome) > 1 else "",
        tipo=Usuario.Tipo.CLIENTE,
        deve_alterar_senha=True,
        password=data_nascimento.strftime("%d%m%Y"),
    )
    return Cliente.objects.create(
        usuario=usuario,
        nome=nome.strip(),
        cpf=cpf,
        data_nascimento=data_nascimento,
        email=email,
        telefone=telefone,
        endereco=endereco,
    )


@transaction.atomic
def atualizar_cliente(*, cliente, nome, email, telefone="", endereco=""):
    telefone = normalizar_telefone(telefone)
    if Usuario.objects.filter(email__iexact=email).exclude(pk=cliente.usuario_id).exists():
        raise ValidationError({"email": "Já existe um usuário cadastrado com este e-mail."})

    cliente.nome = nome.strip()
    cliente.email = email
    cliente.telefone = telefone
    cliente.endereco = endereco
    cliente.save(update_fields=("nome", "email", "telefone", "endereco"))

    if cliente.usuario:
        partes_nome = cliente.nome.split(maxsplit=1)
        cliente.usuario.email = email
        cliente.usuario.first_name = partes_nome[0]
        cliente.usuario.last_name = partes_nome[1] if len(partes_nome) > 1 else ""
        cliente.usuario.save(update_fields=("email", "first_name", "last_name"))
    return cliente
