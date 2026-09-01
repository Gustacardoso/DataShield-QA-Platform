import io
import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_e_listagem_csv() -> None:
    csv_bytes = b"nome,cpf\nJoao,111.222.333-44\nAna,555.666.777-88\n"
    arquivo = io.BytesIO(csv_bytes)

    response = client.post(
        "/api/importacao/upload",
        files={"arquivo": ("clientes.csv", arquivo, "text/csv")},
    )

    assert response.status_code == 200
    corpo = response.json()
    assert corpo["formato"] == "csv"
    assert corpo["num_linhas"] == 2
    assert corpo["colunas"] == ["nome", "cpf"]

    listagem = client.get("/api/importacao/")
    assert listagem.status_code == 200
    assert any(item["id"] == corpo["id"] for item in listagem.json())

    detalhe = client.get(f"/api/importacao/{corpo['id']}")
    assert detalhe.status_code == 200
    assert len(detalhe.json()["preview"]) == 2


def test_upload_json_envelopado_com_dados_aninhados() -> None:
    payload = {
        "usuarios": [
            {
                "nome": "Joao",
                "cpf": "111.222.333-44",
                "endereco": {"cidade": "Osório", "estado": "RS"},
            },
            {
                "nome": "Ana",
                "cpf": "555.666.777-88",
                "endereco": {"cidade": "Porto Alegre", "estado": "RS"},
            },
        ],
        "total_usuarios": 2,
        "observacao": "dados fictícios",
    }
    arquivo = io.BytesIO(json.dumps(payload).encode("utf-8"))

    response = client.post(
        "/api/importacao/upload",
        files={"arquivo": ("usuarios.json", arquivo, "application/json")},
    )

    assert response.status_code == 200
    corpo = response.json()
    assert corpo["num_linhas"] == 2
    assert corpo["colunas"] == ["nome", "cpf", "endereco.cidade", "endereco.estado"]


def test_upload_formato_invalido() -> None:
    arquivo = io.BytesIO(b"conteudo qualquer")

    response = client.post(
        "/api/importacao/upload",
        files={"arquivo": ("arquivo.exe", arquivo, "application/octet-stream")},
    )

    assert response.status_code == 400
