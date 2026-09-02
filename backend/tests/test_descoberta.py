import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _importar_csv_teste() -> int:
    csv_bytes = (
        b"nome,cpf,cidade,email\n"
        b"Joao Silva,111.222.333-44,Osorio,joao@teste.com\n"
        b"Ana Lima,555.666.777-88,Porto Alegre,ana@teste.com\n"
    )
    resposta = client.post(
        "/api/importacao/upload",
        files={"arquivo": ("clientes.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    return resposta.json()["id"]


def test_analisar_arquivo_classifica_colunas_sensiveis() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.post(f"/api/descoberta/{arquivo_id}/analisar")
    assert resposta.status_code == 200

    colunas = {c["nome_coluna"]: c for c in resposta.json()["colunas"]}
    assert colunas["cpf"]["sensivel"] is True
    assert colunas["cpf"]["tipo_dado"] == "CPF"
    assert colunas["email"]["sensivel"] is True
    assert colunas["email"]["tipo_dado"] == "EMAIL"
    assert colunas["nome"]["sensivel"] is True
    assert colunas["cidade"]["sensivel"] is False  # cidade sozinha não identifica ninguém (exemplo do PRD)

    consulta = client.get(f"/api/descoberta/{arquivo_id}")
    assert consulta.status_code == 200
    assert len(consulta.json()["colunas"]) == 4


def test_analisar_arquivo_inexistente_retorna_404() -> None:
    resposta = client.post("/api/descoberta/999999/analisar")
    assert resposta.status_code == 404


def test_obter_analise_sem_analisar_retorna_404() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.get(f"/api/descoberta/{arquivo_id}")
    assert resposta.status_code == 404
