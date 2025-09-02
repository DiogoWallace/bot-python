from fastapi import APIRouter, status, HTTPException
from app.schemas.webhook import WebhookPayload
from app.services import auth_service, logic_service, response_service, external_api_service
from app.database import connection, queries

router = APIRouter()

@router.post("/message", status_code=status.HTTP_200_OK, tags=["Webhook"])
def receive_message(payload: WebhookPayload):
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

        # 5. Gerar e EXECUTAR a query de atualização
        update_query = queries.generate_chat_update_query(
            decision['db_operation_type'], 
            processed_data
        )
        if update_query:
            print(f"\n--- 💾 EXECUTANDO QUERY NO BANCO ---\n{update_query}")
            cursor.execute(update_query)
            conn.commit()
            print("------------------------------------")

    except Exception as e:
        # Erro -> rollback
        conn.rollback()
        print(f"ERRO CRÍTICO: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")
    finally:
        conn.close()
        print("INFO:     Conexão com o banco de dados fechada.")

    return {"status": "ok", "action_taken": decision['next_action']}