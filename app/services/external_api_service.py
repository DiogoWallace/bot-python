from typing import Dict

def send_whatsapp_text(chat_id: str, message: str):
    """
    (SIMULADO) Envia uma mensagem de texto para o usuário via WhatsApp.
    """
    print("\n--- 🚀 ENVIANDO MENSAGEM DE TEXTO ---")
    print(f"Para: {chat_id}")
    print(f"Mensagem: {message}")
    print("------------------------------------")

    return {"status": "simulated_success"}