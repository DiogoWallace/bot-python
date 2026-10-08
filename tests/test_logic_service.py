import pytest

from app.services.logic_service import determine_next_action


def data(has_access=True, valid=True, action="fleet_status"):
    return {"has_access": has_access, "is_valid_command": valid, "command_action": action}


@pytest.mark.parametrize(
    ("processed", "chat_state", "next_action", "db_operation"),
    [
        (data(has_access=False), None, "access_denied", "create_chat_no_access"),
        (data(has_access=False), {"ja_se_apresentou": 1}, "access_denied", "increment_block_count"),
        (data(), None, "send_presentation", "create_chat_with_presentation"),
        (data(), {"ja_se_apresentou": 0}, "send_presentation", "update_presentation"),
        (data(valid=False, action=""), {"ja_se_apresentou": 1}, "invalid_command", "update_activity"),
        (data(action="main_menu"), {"ja_se_apresentou": 1}, "show_main_menu", "update_activity"),
        (data(action="support_request"), {"ja_se_apresentou": 1}, "handle_support_request", "update_activity"),
        (data(action="fleet_status"), {"ja_se_apresentou": 1}, "process_command", "update_activity"),
    ],
)
def test_conversation_state_machine(processed, chat_state, next_action, db_operation):
    assert determine_next_action(processed, chat_state) == {
        "next_action": next_action, "db_operation_type": db_operation
    }
