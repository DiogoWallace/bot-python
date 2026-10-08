import json
import os

# A configuração é lida na importação de app.core.config: o ambiente de teste
# precisa existir antes de qualquer import do app. Valores fictícios.
os.environ.update({
    "DATABASE_URL": "DRIVER={fake};SERVER=fake",
    "EVOLUTION_API_URL": "http://evolution.test",
    "EVOLUTION_API_KEY": "chave-de-teste",
    "WEBHOOK_TOKEN": "token-de-teste",
    "AUTHORIZED_NUMBERS": json.dumps(
        {"5535999999999": {"permission": "gestor", "cluster": "49", "name": "Gestor Teste"}}
    ),
})

import pytest  # noqa: E402

AUTHORIZED = "5535999999999"
UNAUTHORIZED = "5535888888888"


def make_payload(number=AUTHORIZED, text="🚛 Veículos Online", list_title=None):
    message = {"conversation": text}
    if list_title is not None:
        message = {"listResponseMessage": {"title": list_title}}
    return {
        "body": {
            "data": {
                "key": {"remoteJid": f"{number}@c.us", "id": "MSG_1"},
                "pushName": "Contato Teste",
                "message": message,
            },
            "instance": "instancia-teste",
        },
        "event": "messages.upsert",
        "date_time": "2026-10-08T12:00:00Z",
    }


class FakeCursor:
    def __init__(self, conn):
        self.conn = conn
        self.description = None
        self._row = None

    def execute(self, sql, *params):
        self.conn.executed.append((" ".join(sql.split()), params))
        if sql.strip().upper().startswith("SELECT") and self.conn.chat_row:
            self.description = [(name,) for name in self.conn.chat_row]
            self._row = tuple(self.conn.chat_row.values())
        else:
            self._row = None

    def fetchone(self):
        return self._row


class FakeConnection:
    def __init__(self, chat_row=None):
        self.chat_row = chat_row
        self.executed = []
        self.committed = False

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def close(self):
        pass


@pytest.fixture
def payload():
    return make_payload
