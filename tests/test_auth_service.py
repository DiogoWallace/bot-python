from app.schemas.webhook import WebhookPayload
from app.services.auth_service import parse_command, process_webhook

from tests.conftest import AUTHORIZED, UNAUTHORIZED, make_payload


def test_menu_button_maps_to_command():
    assert parse_command("🚛 Veículos Online") == {
        "type": "direct_command", "action": "fleet_status", "params": {}
    }


def test_location_command_extracts_plate():
    cmd = parse_command("local ABC1D23")
    assert cmd["action"] == "location_vehicle"
    assert cmd["params"] == {"plate": "ABC1D23"}


def test_unknown_message_is_not_a_command():
    assert parse_command("oi, tudo bem?")["type"] == "unknown"
    assert parse_command("")["type"] == "unknown"


def test_authorized_number_comes_from_configuration():
    data = process_webhook(WebhookPayload(**make_payload(AUTHORIZED)))
    assert data["has_access"] is True
    assert data["permission"] == "gestor"
    assert data["cluster"] == "49"
    assert data["client_number"] == AUTHORIZED


def test_unknown_number_has_no_access():
    data = process_webhook(WebhookPayload(**make_payload(UNAUTHORIZED)))
    assert data["has_access"] is False
    assert data["permission"] == "no_access"


def test_list_menu_answer_is_read_from_title():
    data = process_webhook(WebhookPayload(**make_payload(list_title="⛽ Abastecimentos")))
    assert data["message"] == "⛽ Abastecimentos"
    assert data["command_action"] == "fuel_current"
