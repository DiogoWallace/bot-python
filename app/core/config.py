from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Classe para gerenciar as configurações da aplicação.
    Lê variáveis de um arquivo .env.
    """
    DATABASE_URL: str
    EVOLUTION_API_URL: str
    EVOLUTION_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()