import re
import unicodedata
from dataclasses import dataclass

import pandas as pd

PALAVRAS_CHAVE: dict[str, list[str]] = {
    "CPF": ["cpf"],
    "RG": ["rg"],
    "CNH": ["cnh"],
    "PASSAPORTE": ["passaporte"],
    "EMAIL": ["email"],
    "TELEFONE": ["telefone", "celular", "fone"],
    "NOME": ["nome"],
    "ENDERECO": ["endereco", "rua", "logradouro", "cep"],
    "DATA_NASCIMENTO": ["nascimento"],
    "CARTAO_CREDITO": ["cartao", "cvv"],
    "SENHA": ["senha"],
    "PIX": ["pix"],
    "DADO_FINANCEIRO": ["salario", "conta", "agencia", "banco"],
}

def _digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor)


_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_DATA_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_CPF_REGEX = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
_CEP_REGEX = re.compile(r"^\d{5}-?\d{3}$")

# Verificadas nesta ordem, só quando o NOME da coluna não deu nenhuma pista
# (ver `classificar_coluna`). Formatos numéricos "puros" colidem entre si (um
# CPF sem formatação e um telefone sem formatação têm os dois 11 dígitos) —
# essa ambiguidade é inerente a olhar só o valor; a ordem abaixo é o critério
# de desempate.
VERIFICACOES_CONTEUDO = [
    ("DATA_NASCIMENTO", lambda v: bool(_DATA_REGEX.match(v))),
    ("EMAIL", lambda v: bool(_EMAIL_REGEX.match(v))),
    ("CEP", lambda v: bool(_CEP_REGEX.match(v)) and len(_digitos(v)) == 8),
    ("CARTAO_CREDITO", lambda v: v.isdigit() and 13 <= len(v) <= 19),
    ("CPF", lambda v: bool(_CPF_REGEX.match(v)) or (v.isdigit() and len(v) == 11)),
    ("TELEFONE", lambda v: len(_digitos(v)) in (10, 11) and not v.isdigit()),
]

TAMANHO_AMOSTRA = 50
LIMIAR_ACERTO = 0.8


@dataclass
class ColunaClassificadaDTO:
    nome_coluna: str
    sensivel: bool
    tipo_dado: str | None


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.lower()


def _tokens(nome_coluna: str) -> list[str]:
    return re.split(r"[._\-\s]+", _normalizar(nome_coluna))


def _tipo_por_nome(nome_coluna: str) -> str | None:
    tokens = _tokens(nome_coluna)
    for tipo, palavras in PALAVRAS_CHAVE.items():
        if any(palavra in tokens for palavra in palavras):
            return tipo
    return None


def _tipo_por_conteudo(valores: pd.Series) -> str | None:
    amostra = valores.dropna().astype(str).str.strip()
    amostra = amostra[amostra != ""].head(TAMANHO_AMOSTRA)
    if amostra.empty:
        return None

    for tipo, verifica in VERIFICACOES_CONTEUDO:
        acertos = amostra.map(verifica)
        if acertos.mean() >= LIMIAR_ACERTO:
            return tipo
    return None


def classificar_coluna(nome_coluna: str, valores: pd.Series) -> ColunaClassificadaDTO:
    tipo_nome = _tipo_por_nome(nome_coluna)
    if tipo_nome is not None:
        return ColunaClassificadaDTO(nome_coluna=nome_coluna, sensivel=True, tipo_dado=tipo_nome)

    tipo_conteudo = _tipo_por_conteudo(valores)
    return ColunaClassificadaDTO(nome_coluna=nome_coluna, sensivel=tipo_conteudo is not None, tipo_dado=tipo_conteudo)


def analisar_dataframe(df: pd.DataFrame) -> list[ColunaClassificadaDTO]:
    return [classificar_coluna(str(coluna), df[coluna]) for coluna in df.columns]
