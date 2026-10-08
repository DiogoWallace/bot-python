import json
from typing import Dict, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Classe para gerenciar as configurações da aplicação.
    Lê variáveis do ambiente ou de um arquivo .env.
    """
    DATABASE_URL: str
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str

    # Token compartilhado com o gateway do WhatsApp. Quando definido, o webhook
    # recusa requisições sem o cabeçalho X-Webhook-Token correspondente.
    WEBHOOK_TOKEN: Optional[str] = None

    # Números autorizados, em JSON:
    # {"5535999999999": {"permission": "gestor", "cluster": "49", "name": "Fulano"}}
    AUTHORIZED_NUMBERS: Dict[str, Dict[str, str]] = {}

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    @field_validator("AUTHORIZED_NUMBERS", mode="before")
    @classmethod
    def parse_authorized_numbers(cls, value):
        if isinstance(value, str):
            return json.loads(value) if value.strip() else {}
        return value


settings = Settings()
