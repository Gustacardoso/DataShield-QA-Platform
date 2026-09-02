import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _importar_csv_teste() -> int:
    csv_bytes = b"nome,cpf,cidade\nJoao Silva,111.222.333-44,Osorio\n"
    resposta = client.post(
        "/api/importacao/upload",
        files={"arquivo": ("clientes.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    return resposta.json()["id"]


def test_aplicar_anonimizacao_padrao_anonimiza_colunas_sensiveis() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.post(f"/api/anonimizacao/{arquivo_id}/aplicar")
    assert resposta.status_code == 200

    corpo = resposta.json()
    assert set(corpo["colunas_anonimizadas"]) == {"nome", "cpf"}

    linha = corpo["preview"][0]
    assert linha["nome"] == "ANONIMO"
    assert linha["cpf"] == "ANONIMO"
    assert linha["cidade"] == "Osorio"  # não sensível, não anonimizada

    download = client.get(f"/api/anonimizacao/{arquivo_id}/download")
    assert download.status_code == 200
    assert b"ANONIMO" in download.content


def test_aplicar_anonimizacao_com_colunas_especificas() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.post(f"/api/anonimizacao/{arquivo_id}/aplicar", json={"colunas": ["cpf"]})
    assert resposta.status_code == 200

    corpo = resposta.json()
    assert corpo["colunas_anonimizadas"] == ["cpf"]
    assert corpo["preview"][0]["nome"] == "Joao Silva"  # não pedido, fica intacto


def test_aplicar_anonimizacao_coluna_inexistente_retorna_400() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.post(f"/api/anonimizacao/{arquivo_id}/aplicar", json={"colunas": ["nao_existe"]})
    assert resposta.status_code == 400


def test_download_sem_anonimizacao_previa_retorna_404() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.get(f"/api/anonimizacao/{arquivo_id}/download")
    assert resposta.status_code == 404
