import re
from collections.abc import Callable

import pandas as pd


def _mascara_generica(valor: str) -> str:
    if len(valor) <= 1:
        return "*" * len(valor)
    return valor[0] + "*" * (len(valor) - 1)


def _mascarar_mantendo_digitos(valor: str, manter_final: int) -> str:
    """Mascara os dígitos do valor, preservando pontuação (ex: '.', '-') no
    lugar e mantendo os últimos `manter_final` dígitos visíveis."""
    total_digitos = sum(1 for c in valor if c.isdigit())
    a_mascarar = max(total_digitos - manter_final, 0)

    resultado = []
    vistos = 0
    for c in valor:
        if not c.isdigit():
            resultado.append(c)
            continue
        resultado.append("*" if vistos < a_mascarar else c)
        vistos += 1
    return "".join(resultado)


def _mascarar_email(valor: str) -> str:
    if "@" not in valor:
        return _mascara_generica(valor)
    usuario, dominio = valor.split("@", 1)
    if len(usuario) <= 1:
        usuario_mascarado = "*" * len(usuario)
    else:
        usuario_mascarado = usuario[0] + "*" * (len(usuario) - 1)
    return f"{usuario_mascarado}@{dominio}"


def _mascarar_senha(_valor: str) -> str:
    # Tamanho fixo sempre — nunca expõe nem o comprimento da senha original.
    return "********"


def _mascarar_cvv(_valor: str) -> str:
    # CVV é curto (3-4 dígitos): "manter os últimos N" não faz sentido aqui,
    # esconderia pouco ou nada. Mascara tudo, sempre, igual senha.
    return "***"


_DATA_REGEX = re.compile(r"^(\d{4})-\d{2}-\d{2}$")


def _mascarar_data_nascimento(valor: str) -> str:
    encontrado = _DATA_REGEX.match(valor)
    if encontrado:
        return f"{encontrado.group(1)}-**-**"
    return _mascara_generica(valor)


def _mascarar_nome(valor: str) -> str:
    palavras = valor.split(" ")
    mascaradas = [palavra if len(palavra) <= 1 else palavra[0] + "*" * (len(palavra) - 1) for palavra in palavras]
    return " ".join(mascaradas)


MASCARADORES: dict[str, Callable[[str], str]] = {
    "CPF": lambda v: _mascarar_mantendo_digitos(v, manter_final=2),
    "TELEFONE": lambda v: _mascarar_mantendo_digitos(v, manter_final=4),
    "CEP": lambda v: _mascarar_mantendo_digitos(v, manter_final=5),
    "CARTAO_CREDITO": lambda v: _mascarar_mantendo_digitos(v, manter_final=4),
    "EMAIL": _mascarar_email,
    "SENHA": _mascarar_senha,
    "CVV": _mascarar_cvv,
    "DATA_NASCIMENTO": _mascarar_data_nascimento,
    "NOME": _mascarar_nome,
}


def mascarar_valor(tipo_dado: str | None, valor: object) -> object:
    if pd.isna(valor):
        return valor

    mascarador = MASCARADORES.get(tipo_dado or "", _mascara_generica)
    return mascarador(str(valor))


def mascarar_dataframe(df: pd.DataFrame, colunas: list[str], tipos: dict[str, str | None]) -> pd.DataFrame:
    resultado = df.copy()
    for coluna in colunas:
        if coluna not in resultado.columns:
            continue
        tipo = tipos.get(coluna)
        resultado[coluna] = resultado[coluna].map(lambda valor, tipo=tipo: mascarar_valor(tipo, valor))
    return resultado
