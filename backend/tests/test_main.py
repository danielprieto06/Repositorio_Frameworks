
import sys
from pathlib import Path

# Añadir la carpeta backend al path de Python
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_inicio():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "mensaje": "Bienvenido a FitLife"
    }


def test_cabecera_tiempo():
    response = client.get("/")

    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    assert float(response.headers["X-Process-Time"]) >= 0


def test_cors_preflight():
    response = client.options(
        "/users/admin/users/1/role",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "Authorization,Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == (
        "http://localhost:3000"
    )
    assert "PATCH" in response.headers.get(
        "access-control-allow-methods", ""
    )

def test_ruta_protegida_sin_token():
    response = client.get("/workouts/")

    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_registro_datos_invalidos():
    response = client.post(
        "/users/",
        json={
            "username": "ab",
            "email": "correo_invalido",
            "password": "123"
        },
    )

    assert response.status_code == 422
