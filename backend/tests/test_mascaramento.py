import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _importar_csv_teste() -> int:
    csv_bytes = b"nome,cpf,email,cidade\nJoao Silva,111.222.333-44,joao@teste.com,Osorio\n"
    resposta = client.post(
        "/api/importacao/upload",
        files={"arquivo": ("clientes.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    return resposta.json()["id"]


def test_aplicar_mascaramento_padrao_mascara_colunas_sensiveis() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.post(f"/api/mascaramento/{arquivo_id}/aplicar")
    assert resposta.status_code == 200

    corpo = resposta.json()
    assert set(corpo["colunas_mascaradas"]) == {"nome", "cpf", "email"}

    linha = corpo["preview"][0]
    assert linha["cpf"] == "***.***.***-44"
    assert linha["email"] == "j***@teste.com"
    assert linha["nome"] == "J*** S****"
    assert linha["cidade"] == "Osorio"  # não sensível, não mascarada

    download = client.get(f"/api/mascaramento/{arquivo_id}/download")
    assert download.status_code == 200
    assert b"***" in download.content


def test_aplicar_mascaramento_com_colunas_especificas() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.post(f"/api/mascaramento/{arquivo_id}/aplicar", json={"colunas": ["cpf"]})
    assert resposta.status_code == 200

    corpo = resposta.json()
    assert corpo["colunas_mascaradas"] == ["cpf"]
    assert corpo["preview"][0]["email"] == "joao@teste.com"  # não pedido, fica intacto


def test_aplicar_mascaramento_coluna_inexistente_retorna_400() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.post(f"/api/mascaramento/{arquivo_id}/aplicar", json={"colunas": ["nao_existe"]})
    assert resposta.status_code == 400


def test_download_sem_mascaramento_previo_retorna_404() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.get(f"/api/mascaramento/{arquivo_id}/download")
    assert resposta.status_code == 404
