from fastapi import FastAPI
from app.api import endpoints

app = FastAPI(
    title="Darwin Chatbot API",
    description="API para o chatbot de gestão de frotas Darwin.",
    version="1.0.0"
)

app.include_router(endpoints.router)

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint principal para verificar se a API está online."""
    return {"status": "Darwin Chatbot API is running!"}