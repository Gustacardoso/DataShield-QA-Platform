import random
import re
import unicodedata
from collections.abc import Callable

import pandas as pd
from faker import Faker

fake = Faker("pt_BR")

BANCOS_BR = ["Banco do Brasil", "Bradesco", "Itaú", "Santander", "Caixa Econômica", "Nubank", "Inter"]

GERADORES_POR_PALAVRA: dict[str, Callable[[], object]] = {
    "cpf": fake.cpf,
    "rg": fake.rg,
    "cnh": lambda: str(fake.random_number(digits=11, fix_len=True)),
    "passaporte": lambda: f"P{fake.random_number(digits=6, fix_len=True)}",
    "email": fake.email,
    "telefone": fake.phone_number,
    "celular": fake.phone_number,
    "fone": fake.phone_number,
    "nome": fake.name,
    "rua": fake.street_name,
    "logradouro": fake.street_name,
    "endereco": fake.street_address,
    "cidade": fake.city,
    "estado": fake.state_abbr,
    "cep": fake.postcode,
    "nascimento": lambda: fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
    "cartao": fake.credit_card_number,
    "cvv": fake.credit_card_security_code,
    "senha": lambda: fake.password(length=12),
    "pix": fake.email,
    "salario": lambda: round(random.uniform(1800, 20000), 2),
    "conta": lambda: f"{fake.random_number(digits=5, fix_len=True)}-{random.randint(0, 9)}",
    "agencia": lambda: str(fake.random_number(digits=4, fix_len=True)),
    "banco": lambda: random.choice(BANCOS_BR),
    "cargo": fake.job,
    "empresa": fake.company,
}


def _tokens(nome_coluna: str) -> list[str]:
    sem_acento = unicodedata.normalize("NFKD", nome_coluna).encode("ascii", "ignore").decode("ascii")
    return re.split(r"[._\-\s]+", sem_acento.lower())


def _valor_generico(dtype: object) -> object:
    if pd.api.types.is_numeric_dtype(dtype):
        return fake.random_int(min=0, max=100_000)
    return fake.word()


def gerar_valor_coluna(nome_coluna: str, dtype: object) -> object:
    # Em nome composto (ex: "endereco.cidade", "conta_bancaria.banco") o
    # último token é o mais específico — checar nessa ordem evita que
    # "endereco" capture uma coluna de cidade/estado/cep antes da hora.
    tokens = reversed(_tokens(nome_coluna))
    for token in tokens:
        gerador = GERADORES_POR_PALAVRA.get(token)
        if gerador is not None:
            return gerador()
    return _valor_generico(dtype)


def gerar_dataframe_sintetico(colunas: list[str], dtypes: dict[str, object], num_linhas: int) -> pd.DataFrame:
    dados = {coluna: [gerar_valor_coluna(coluna, dtypes.get(coluna)) for _ in range(num_linhas)] for coluna in colunas}
    return pd.DataFrame(dados, columns=colunas)
