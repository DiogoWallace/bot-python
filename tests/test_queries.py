import pytest

from app.database.queries import generate_chat_update_query

OPERATIONS = [
    "create_chat_no_access",
    "increment_block_count",
    "create_chat_with_presentation",
    "update_presentation",
    "update_activity",
]


@pytest.mark.parametrize("operation", OPERATIONS)
def test_every_value_goes_as_parameter(operation):
    hostile_id = "x'; DROP TABLE t_pbi_interacoes_chatbot; --"
    sql, params = generate_chat_update_query(
        operation, {"chat_id": hostile_id, "client_name": "O'Brien"}
    )
    assert sql.count("?") == len(params)
    assert hostile_id in params
    assert hostile_id not in sql
    assert "O'Brien" not in sql


def test_unknown_operation_generates_nothing():
    assert generate_chat_update_query("none", {"chat_id": "1"}) is None
