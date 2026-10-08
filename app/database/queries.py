import pyodbc
from typing import Dict, Any, Optional, Tuple

def get_chat_state(conn: pyodbc.Connection, chat_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca o estado atual da conversa de um usuário no banco de dados.
    Corresponde ao nó 'get_chat' do n8n.
    """
    query = """
        SELECT 
            *
        FROM t_pbi_interacoes_chatbot 
        WHERE chat_id = ?;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query, chat_id)
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        return None
    except pyodbc.Error as e:
        print(f"ERRO ao buscar estado do chat: {e}")
        return None

def generate_chat_update_query(
    operation_type: str, data: Dict[str, Any]
) -> Optional[Tuple[str, Tuple[Any, ...]]]:
    """
    Gera a query SQL de INSERT ou UPDATE para o estado da conversa, com os
    valores separados como parâmetros: nada que vem do webhook entra no texto
    do SQL. Corresponde à lógica do nó 'database_record_manager' do n8n.
    """
    chat_id = data.get('chat_id')
    client_name = data.get('client_name', '')

    queries = {
        'create_chat_no_access': (
            """
            INSERT INTO t_pbi_interacoes_chatbot (chat_id, nome, ja_se_apresentou, encerrado, ultima_interacao, count_bloqueio)
            VALUES (?, ?, 0, 0, GETDATE(), 1);
            """,
            (chat_id, client_name),
        ),
        'increment_block_count': (
            """
            UPDATE t_pbi_interacoes_chatbot
            SET count_bloqueio = count_bloqueio + 1, ultima_interacao = GETDATE()
            WHERE chat_id = ?;
            """,
            (chat_id,),
        ),
        'create_chat_with_presentation': (
            """
            INSERT INTO t_pbi_interacoes_chatbot (chat_id, nome, ja_se_apresentou, encerrado, aviso_enviado, ultima_interacao, count_bloqueio)
            VALUES (?, ?, 1, 0, 0, GETDATE(), 0);
            """,
            (chat_id, client_name),
        ),
        'update_presentation': (
            """
            UPDATE t_pbi_interacoes_chatbot
            SET ja_se_apresentou = 1, encerrado = 0, aviso_enviado = 0, ultima_interacao = GETDATE(), count_bloqueio = 0
            WHERE chat_id = ?;
            """,
            (chat_id,),
        ),
        'update_activity': (
            """
            UPDATE t_pbi_interacoes_chatbot
            SET encerrado = 0, ultima_interacao = GETDATE(), aviso_enviado = 0
            WHERE chat_id = ?;
            """,
            (chat_id,),
        ),
    }
    return queries.get(operation_type)