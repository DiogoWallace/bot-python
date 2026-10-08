import hmac
from typing import Optional

from fastapi import APIRouter, Header, status, HTTPException
from app.core.config import settings
from app.schemas.webhook import WebhookPayload
from app.services import auth_service, logic_service, response_service, external_api_service
from app.database import connection, queries

router = APIRouter()


def check_webhook_token(token: Optional[str]) -> None:
    """Recusa a chamada quando WEBHOOK_TOKEN está definido e o cabeçalho não confere."""
    expected = settings.WEBHOOK_TOKEN
    if expected and not (token and hmac.compare_digest(token, expected)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook token")


@router.post("/message", status_code=status.HTTP_200_OK, tags=["Webhook"])
def receive_message(
    payload: WebhookPayload,
    x_webhook_token: Optional[str] = Header(default=None),
):
    check_webhook_token(x_webhook_token)
    processed_data = auth_service.process_webhook(payload)
    
    conn = connection.get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="Database connection unavailable")

    try:
        cursor = conn.cursor()
        
        # 1. Buscar estado do chat
        chat_state = queries.get_chat_state(conn, processed_data['chat_id'])

        # 2. Determinar a próxima ação
        decision = logic_service.determine_next_action(processed_data, chat_state)
        
        # 3. Gerar a resposta para o usuário
        response = response_service.generate_response(decision['next_action'], chat_state)

        # 4. Enviar a resposta (simulado)
        if response.get("text_message"):
            external_api_service.send_whatsapp_text(
                chat_id=processed_data['chat_id'],
                message=response['text_message']
            )

        # 5. Gerar e EXECUTAR a query de atualização (valores como parâmetros)
        update = queries.generate_chat_update_query(
            decision['db_operation_type'],
            processed_data
        )
        if update:
            sql, params = update
            print(f"INFO:     Atualizando estado do chat ({decision['db_operation_type']}).")
            cursor.execute(sql, *params)
            conn.commit()

    except Exception as e:
        # Erro -> rollback
        conn.rollback()
        print(f"ERRO CRÍTICO: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")
    finally:
        conn.close()
        print("INFO:     Conexão com o banco de dados fechada.")

    return {"status": "ok", "action_taken": decision['next_action']}