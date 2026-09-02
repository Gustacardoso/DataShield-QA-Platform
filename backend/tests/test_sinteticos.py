import io
import re

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

CPF_ORIGINAL = "111.222.333-44"


def _importar_csv_teste() -> int:
    csv_bytes = f"nome,cpf,cidade,salario\nJoao Silva,{CPF_ORIGINAL},Osorio,5000\n".encode()
    resposta = client.post(
        "/api/importacao/upload",
        files={"arquivo": ("clientes.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    return resposta.json()["id"]


def test_gerar_sinteticos_com_estrutura_igual_sem_dado_real() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.post(f"/api/sinteticos/{arquivo_id}/gerar", json={"num_linhas": 20})
    assert resposta.status_code == 200

    corpo = resposta.json()
    assert corpo["num_linhas"] == 20
    assert len(corpo["preview"]) == 10

    for linha in corpo["preview"]:
        assert set(linha.keys()) == {"nome", "cpf", "cidade", "salario"}
        assert re.match(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", linha["cpf"])
        assert linha["cpf"] != CPF_ORIGINAL  # nenhum dado real vaza
        assert linha["nome"] != "Joao Silva"

    download = client.get(f"/api/sinteticos/{arquivo_id}/download")
    assert download.status_code == 200
    assert CPF_ORIGINAL.encode() not in download.content


def test_gerar_sinteticos_num_linhas_invalido_retorna_422() -> None:
    arquivo_id = _importar_csv_teste()

    assert client.post(f"/api/sinteticos/{arquivo_id}/gerar", json={"num_linhas": 0}).status_code == 422
    assert client.post(f"/api/sinteticos/{arquivo_id}/gerar", json={"num_linhas": 100_000}).status_code == 422


def test_download_sem_geracao_previa_retorna_404() -> None:
    arquivo_id = _importar_csv_teste()

    resposta = client.get(f"/api/sinteticos/{arquivo_id}/download")
    assert resposta.status_code == 404
