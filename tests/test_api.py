"""API-level tests for the HTTP endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "VoxPilot",
        "version": "0.1.0",
    }


def test_speak_recognized_command(client):
    response = client.post("/speak", json={"command": "camina hacia adelante"})

    assert response.status_code == 200
    assert response.json() == {
        "recognized": True,
        "action": "caminó hacia adelante",
    }


def test_speak_unknown_command(client):
    response = client.post("/speak", json={"command": "salta"})

    assert response.status_code == 200
    assert response.json() == {"recognized": False, "action": None}


def test_speak_missing_command_returns_422(client):
    response = client.post("/speak", json={})

    assert response.status_code == 422


def test_response_includes_correlation_id_header(client):
    response = client.post("/speak", json={"command": "camina hacia adelante"})

    assert response.headers.get("X-Request-ID")
