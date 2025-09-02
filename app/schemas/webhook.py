from pydantic import BaseModel, Field
from typing import Optional

class WebhookKey(BaseModel):
    remote_jid: str = Field(..., alias='remoteJid')
    id: str

class WebhookMessage(BaseModel):
    conversation: Optional[str] = None
    list_response_message: Optional[dict] = Field(None, alias='listResponseMessage')

class WebhookData(BaseModel):
    key: WebhookKey
    push_name: str = Field(..., alias='pushName')
    message: WebhookMessage

class WebhookBody(BaseModel):
    webhook_data: WebhookData = Field(..., alias='data')
    instance: str

class WebhookPayload(BaseModel):
    """Modelo principal para o payload do webhook."""
    body: WebhookBody
    event: str
    date_time: str = Field(..., alias='date_time')