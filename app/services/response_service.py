from typing import Dict, Any, Optional

def generate_response(next_action: str, chat_state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gera a resposta a ser enviada ao usuário com base na ação decidida.
    """
    response = {
        "text_message": None,
        "menu_json": None,
        "contact": None,
        "block_user": False
    }

    if next_action == "access_denied":
        count_bloqueio = chat_state.get('count_bloqueio', 0) if chat_state else 0
        
        if count_bloqueio == 0:
            response["text_message"] = (
                "Olá!\n\nSou o Darwin, seu assistente virtual especializado em condução eficiente de caminhões.\n\n"
                "No momento, seu número ainda não está autorizado para utilizar este serviço.\n\n"
                "Para solicitar o acesso, entre em contato com a sua supervisão e peça a liberação.\n\n"
                "Assim que for autorizado, estarei pronto para te ajudar na estrada! 🚛"
            )
            response["contact"] = True
        elif count_bloqueio < 3:
            response["text_message"] = (
                "Atenção: Seu número não possui permissão para acessar este serviço.\n\n"
                "Por segurança, caso continue tentando, seu número será bloqueado. "
                "Para solicitar acesso, fale com seu supervisor."
            )
        else:
            response["text_message"] = "🚫 Acesso negado.\n\nSeu número foi bloqueado por excesso de tentativas de acesso sem permissão."
            response["block_user"] = True

    
    return response