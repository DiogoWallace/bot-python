from datetime import datetime, timezone
from typing import Dict, Any
from app.core.config import settings
from app.schemas.webhook import WebhookPayload

# ===================================
# Mapeamento de Comandos (do n8n)
# ===================================
# Os números autorizados vêm de AUTHORIZED_NUMBERS (.env), não do código.

CONFIG = {
  "COMMAND_MAPPING": {
    "🚛 Veículos Online": "fleet_status",
    "🕒 Veículos Parados com Motor Ligado": "vehicles_idle_on",
    "📊 Desempenho da Frota": "performance",
    "💬 Falar com um Atendente": "support_request",
    "⛽ Abastecimentos": "fuel_current",
    "📆 Resumo da Jornada": "journey_current",
    "Voltar": "main_menu",
  }
}

# ===================================
# Funções Utilitárias (Tradução do JS)
# ===================================

def extract_phone_number(remote_jid: str) -> str:
    """Extrai o número de telefone de um JID do WhatsApp."""
    return remote_jid.split("@")[0] if remote_jid else ""

def parse_command(message: str) -> dict:
    """Analisa a mensagem para determinar o tipo e a ação do comando."""
    if not message:
        return {"type": "unknown", "action": "", "params": {}}
    
    clean_message = message.strip()

    if clean_message.lower().startswith("local "):
        plate = clean_message[6:].strip()
        return {
            "type": "location_specific",
            "action": "location_vehicle",
            "params": {"plate": plate}
        }
    
    action = CONFIG["COMMAND_MAPPING"].get(clean_message)
    if action:
        return {"type": "direct_command", "action": action, "params": {}}
        
    return {"type": "unknown", "action": "", "params": {}}

# ===================================
# Lógica Principal de Processamento
# ===================================

def process_webhook(payload: WebhookPayload) -> Dict[str, Any]:
    """Processa o payload do webhook e retorna um dicionário estruturado."""
    
    user_message = ""
    if payload.body.webhook_data.message.conversation:
        user_message = payload.body.webhook_data.message.conversation
    elif payload.body.webhook_data.message.list_response_message:
        user_message = payload.body.webhook_data.message.list_response_message.get("title", "")

    chat_id = payload.body.webhook_data.key.remote_jid
    phone_number = extract_phone_number(chat_id)
    
    user_config = settings.AUTHORIZED_NUMBERS.get(phone_number, {})
    permission = user_config.get("permission", "no_access")
    cluster = user_config.get("cluster", "")
    
    command_info = parse_command(user_message)

    processed_data = {
        "instancia": payload.body.instance,
        "chat_id": chat_id,
        "message_id": payload.body.webhook_data.key.id,
        "client_name": payload.body.webhook_data.push_name,
        "client_number": phone_number,
        "event": payload.event,
        "message": user_message,
        "permission": permission,
        "cluster": cluster,
        "has_access": permission != "no_access",
        "command_type": command_info["type"],
        "command_action": command_info["action"],
        "command_params": command_info["params"],
        "is_valid_command": command_info["type"] != "unknown",
        "processed_at_utc": datetime.now(timezone.utc).isoformat()
    }

    return processed_data