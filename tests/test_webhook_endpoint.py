import pytest
from fastapi.testclient import TestClient

from app.database import connection
from app.main import app

from tests.conftest import AUTHORIZED, UNAUTHORIZED, FakeConnection, make_payload

client = TestClient(app)
TOKEN = {"X-Webhook-Token": "token-de-teste"}


@pytest.fixture
def fake_db(monkeypatch):
    def install(chat_row=None):
        conn = FakeConnection(chat_row)
        monkeypatch.setattr(connection, "get_db_connection", lambda: conn)
        return conn
    return install


def test_rejects_call_without_token(fake_db):
    fake_db()
    assert client.post("/message", json=make_payload()).status_code == 401


def test_rejects_wrong_token(fake_db):
    fake_db()
    r = client.post("/message", json=make_payload(), headers={"X-Webhook-Token": "errado"})
    assert r.status_code == 401


def test_first_contact_of_authorized_user_gets_presentation(fake_db):
    conn = fake_db(chat_row=None)
    r = client.post("/message", json=make_payload(AUTHORIZED), headers=TOKEN)
    assert r.status_code == 200
    assert r.json()["action_taken"] == "send_presentation"
    sql, params = conn.executed[-1]
    assert sql.startswith("INSERT INTO t_pbi_interacoes_chatbot")
    assert params == (f"{AUTHORIZED}@c.us", "Contato Teste")
    assert conn.committed


def test_unauthorized_user_increments_block_count(fake_db):
    conn = fake_db(chat_row={"chat_id": f"{UNAUTHORIZED}@c.us", "ja_se_apresentou": 0, "count_bloqueio": 3})
    r = client.post("/message", json=make_payload(UNAUTHORIZED), headers=TOKEN)
    assert r.json()["action_taken"] == "access_denied"
    sql, params = conn.executed[-1]
    assert "count_bloqueio = count_bloqueio + 1" in sql
    assert params == (f"{UNAUTHORIZED}@c.us",)


def test_database_unavailable_returns_503(monkeypatch):
    monkeypatch.setattr(connection, "get_db_connection", lambda: None)
    r = client.post("/message", json=make_payload(), headers=TOKEN)
    assert r.status_code == 503
