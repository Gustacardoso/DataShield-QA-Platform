import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _importar_csv_teste() -> int:
    csv_bytes = b"nome,cpf,cidade\nJoao Silva,111.222.333-44,Osorio\nAna Lima,555.666.777-88,Porto Alegre\n"
    resposta = client.post(
        "/api/importacao/upload",
        files={"arquivo": ("clientes.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    return resposta.json()["id"]


def test_avaliacao_antes_do_tratamento_e_risco_alto() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.get(f"/api/lgpd/{arquivo_id}")
    assert resposta.status_code == 200

    corpo = resposta.json()
    assert corpo["nivel_risco"] == "Alto"
    assert corpo["total_colunas_sensiveis"] == 2  # nome, cpf
    assert corpo["colunas_tratadas"] == 0

    encontrados = {d["coluna"]: d for d in corpo["dados_encontrados"]}
    assert encontrados["cpf"]["quantidade_encontrada"] == 2
    assert encontrados["cpf"]["tratado"] is False
    assert "cidade" not in encontrados  # não sensível, não entra no relatório


def test_avaliacao_apos_mascarar_tudo_e_risco_baixo() -> None:
    arquivo_id = _importar_csv_teste()

    client.post(f"/api/mascaramento/{arquivo_id}/aplicar", json={"colunas": ["cpf", "nome"]})

    resposta = client.get(f"/api/lgpd/{arquivo_id}")
    corpo = resposta.json()
    assert corpo["nivel_risco"] == "Baixo"
    assert corpo["colunas_tratadas"] == 2


def test_avaliacao_com_tratamento_parcial_e_risco_medio() -> None:
    arquivo_id = _importar_csv_teste()

    client.post(f"/api/mascaramento/{arquivo_id}/aplicar", json={"colunas": ["cpf"]})

    resposta = client.get(f"/api/lgpd/{arquivo_id}")
    corpo = resposta.json()
    assert corpo["nivel_risco"] == "Médio"


def test_avaliacao_arquivo_inexistente_retorna_404() -> None:
    resposta = client.get("/api/lgpd/999999")
    assert resposta.status_code == 404
