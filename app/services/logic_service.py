from typing import Dict, Any, Optional

def determine_next_action(
    processed_data: Dict[str, Any], 
    chat_state: Optional[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Determina a próxima ação e a operação de banco de dados necessária.
    Corresponde ao nó 'Logic_bot' do n8n.
    """
    has_access = processed_data.get('has_access', False)
    is_valid_command = processed_data.get('is_valid_command', False)
    command_action = processed_data.get('command_action', '')
    
    chat_exists = chat_state is not None
    has_been_presented = chat_state.get('ja_se_apresentou', False) if chat_state else False

    next_action = "unknown"
    db_operation_type = "none"

    # Cenário 1: Usuário sem acesso
    if not has_access:
        next_action = "access_denied"
        db_operation_type = "increment_block_count" if chat_exists else "create_chat_no_access"
    
    # Cenário 2: Primeira interação ou usuário que não viu a apresentação
    elif not chat_exists or not has_been_presented:
        next_action = "send_presentation"
        db_operation_type = "update_presentation" if chat_exists else "create_chat_with_presentation"

    # Cenário 3: Comando inválido
    elif not is_valid_command:
        next_action = "invalid_command"
        db_operation_type = "update_activity"
    
    # Cenário 4: Comando válido de um usuário autenticado
    else:
        db_operation_type = "update_activity"
        if command_action == "main_menu":
            next_action = "show_main_menu"
        elif command_action == "support_request":
            next_action = "handle_support_request"
        else:
            next_action = "process_command"
            
    return {"next_action": next_action, "db_operation_type": db_operation_type}