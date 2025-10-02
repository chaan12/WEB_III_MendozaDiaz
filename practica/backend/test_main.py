import pytest
import mongomock
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)
fake_mongo_client = mongomock.MongoClient()
fake_database = fake_mongo_client.practica1
fake_collection_historial = fake_database.historial

# --------- SUMA ----------
@pytest.mark.parametrize("numeros, resultado", [
    ([5, 10], 15),
    ([0, 0], 0),
    ([2.5, 2.5], 5.0),
])
def test_sumar(monkeypatch, numeros, resultado):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)

    response = client.post("/calculadora/sum", json={"cantidad": len(numeros), "numeros": numeros})
    assert response.status_code == 200
    assert response.json()["resultado"] == resultado
    assert fake_collection_historial.find_one({"resultado": resultado}) is not None

# --------- RESTA ----------
@pytest.mark.parametrize("numeros, resultado", [
    ([10, 5], 5),
    ([5, 5, 5], -5),
])
def test_restar(monkeypatch, numeros, resultado):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)

    response = client.post("/calculadora/resta", json={"cantidad": len(numeros), "numeros": numeros})
    assert response.status_code == 200
    assert response.json()["resultado"] == resultado

# --------- MULTIPLICACIÓN ----------
@pytest.mark.parametrize("numeros, resultado", [
    ([2, 3], 6),
    ([2, 3, 4], 24),
    ([10, 0], 0),
])
def test_multiplicar(monkeypatch, numeros, resultado):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)

    response = client.post("/calculadora/multiplicacion", json={"cantidad": len(numeros), "numeros": numeros})
    assert response.status_code == 200
    assert response.json()["resultado"] == resultado

# --------- DIVISIÓN ----------
@pytest.mark.parametrize("numeros, resultado", [
    ([10, 2], 5),
    ([100, 2, 5], 10),
])
def test_dividir(monkeypatch, numeros, resultado):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)

    response = client.post("/calculadora/division", json={"cantidad": len(numeros), "numeros": numeros})
    assert response.status_code == 200
    assert response.json()["resultado"] == resultado

def test_dividir_por_cero(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)

    response = client.post("/calculadora/division", json={"cantidad": 2, "numeros": [10, 0]})
    assert response.status_code == 400 or response.status_code == 403
    assert "cero" in response.json()["detail"].lower()

# --------- VALIDACIONES ----------
def test_menos_de_dos_operandos(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)

    response = client.post("/calculadora/sum", json={"cantidad": 1, "numeros": [5]})
    assert response.status_code == 400
    assert "operandos" in response.json()["detail"].lower()

def test_no_numeros(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)

    response = client.post("/calculadora/sum", json={"cantidad": 2, "numeros": ["hola", 5]})
    assert response.status_code == 422  # Error de validación de Pydantic

# --------- HISTORIAL ----------
def test_historial(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)

    # Insertamos operaciones previas
    client.post("/calculadora/sum", json={"cantidad": 2, "numeros": [1, 2]})
    client.post("/calculadora/resta", json={"cantidad": 2, "numeros": [5, 3]})

    response = client.get("/calculadora/historial")
    assert response.status_code == 200
    data = response.json()["historial"]
    assert len(data) >= 2
    assert any(op["operacion"] == "suma" for op in data)
    assert any(op["operacion"] == "resta" for op in data)

def test_historial_filtro_operacion(monkeypatch):
    monkeypatch.setattr(main, "collection_historial", fake_collection_historial)

    client.post("/calculadora/sum", json={"cantidad": 2, "numeros": [1, 2]})
    client.post("/calculadora/resta", json={"cantidad": 2, "numeros": [5, 3]})

    response = client.get("/calculadora/historial?operacion=suma")
    assert response.status_code == 200
    data = response.json()["historial"]
    assert all(op["operacion"] == "suma" for op in data)