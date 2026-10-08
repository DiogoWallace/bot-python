# Bot de frotas para WhatsApp — FastAPI + SQL Server

[![CI](https://github.com/DiogoWallace/bot-python/actions/workflows/ci.yml/badge.svg)](https://github.com/DiogoWallace/bot-python/actions/workflows/ci.yml)

Backend de um assistente de gestão de frotas no WhatsApp. Recebe as mensagens
pelo webhook da [Evolution API](https://github.com/EvolutionAPI/evolution-api),
autoriza o número, interpreta o comando do menu, consulta o estado da conversa
no SQL Server e decide a próxima ação.

É a reescrita em Python de um fluxo que rodava no **n8n**: cada nó do fluxo
virou uma função testável (`get_chat`, `Logic_bot`, `database_record_manager`).

> **Status: protótipo.** O ciclo de entrada está pronto e testado — webhook,
> autorização, comandos, máquina de estados e persistência do estado da
> conversa. A saída ainda não: o envio para o WhatsApp é **simulado** (registra
> no log) e, das respostas, só a de acesso negado está escrita. Ver
> [Próximos passos](#próximos-passos).

## Como funciona

```text
WhatsApp ──▶ Evolution API ──webhook──▶ POST /message
                                          │  1. confere o X-Webhook-Token
                                          │  2. extrai número e comando
                                          │  3. número está em AUTHORIZED_NUMBERS?
                                          │  4. lê o estado da conversa (SQL Server)
                                          │  5. máquina de estados → próxima ação
                                          │  6. monta a resposta e envia (simulado)
                                          └  7. grava o novo estado (SQL parametrizado)
```

### Máquina de estados

| Situação | Próxima ação | O que grava |
|---|---|---|
| Número não autorizado, primeira vez | `access_denied` | cria a conversa com 1 bloqueio |
| Número não autorizado, de novo | `access_denied` (aviso; bloqueio a partir da 4ª tentativa) | incrementa o contador de bloqueio |
| Autorizado, primeiro contato | `send_presentation` | cria a conversa já apresentada |
| Autorizado, ainda não apresentado | `send_presentation` | marca como apresentado |
| Comando desconhecido | `invalid_command` | atualiza a última interação |
| `Voltar` | `show_main_menu` | atualiza a última interação |
| `💬 Falar com um Atendente` | `handle_support_request` | atualiza a última interação |
| Demais comandos | `process_command` | atualiza a última interação |

### Comandos reconhecidos

| Mensagem (botão do menu) | Ação |
|---|---|
| 🚛 Veículos Online | `fleet_status` |
| 🕒 Veículos Parados com Motor Ligado | `vehicles_idle_on` |
| 📊 Desempenho da Frota | `performance` |
| ⛽ Abastecimentos | `fuel_current` |
| 📆 Resumo da Jornada | `journey_current` |
| 💬 Falar com um Atendente | `support_request` |
| `local <placa>` | `location_vehicle` (com a placa extraída) |

## Segurança

- **SQL sempre parametrizado.** Nenhum valor vindo do webhook entra no texto do
  SQL; os testes mandam um `chat_id` hostil (`x'; DROP TABLE ...`) e conferem
  que ele só aparece nos parâmetros.
- **Números autorizados fora do código**, em `AUTHORIZED_NUMBERS` no `.env`,
  com permissão e cluster de cada um.
- **Webhook autenticado:** com `WEBHOOK_TOKEN` definido, chamadas sem o
  cabeçalho `X-Webhook-Token` correto recebem 401 (comparação em tempo
  constante).
- **Bloqueio progressivo** de números sem permissão que insistem.
- A gravação no banco registra no log só o tipo de operação, não o SQL
  preenchido com os dados da conversa.

## Stack

Python 3.12 · FastAPI · Pydantic / pydantic-settings · pyodbc (SQL Server) ·
pytest · GitHub Actions

```
app/
├── api/endpoints.py            # POST /message: o fluxo inteiro
├── core/config.py              # configuração (.env), incluindo números e token
├── database/
│   ├── connection.py           # conexão pyodbc
│   └── queries.py              # leitura e gravação do estado da conversa
├── schemas/webhook.py          # payload da Evolution API (Pydantic)
└── services/
    ├── auth_service.py         # número, permissão e comando
    ├── logic_service.py        # máquina de estados
    ├── response_service.py     # texto das respostas
    └── external_api_service.py # envio ao WhatsApp (simulado)
tests/                          # 25 testes, com banco falso
```

## Rodando localmente

Pré-requisitos: Python 3.12, acesso a um SQL Server e o
[ODBC Driver 18 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server).

```bash
git clone https://github.com/DiogoWallace/bot-python.git
cd bot-python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # preencha conexão, Evolution API, token e números
uvicorn app.main:app --reload
```

A documentação interativa fica em `http://127.0.0.1:8000/docs`. Uma chamada de
exemplo, com número fictício:

```bash
curl -X POST http://127.0.0.1:8000/message \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: $WEBHOOK_TOKEN" \
  -d '{
    "body": {
      "data": {
        "key": {"remoteJid": "5535999999999@c.us", "id": "MSG_1"},
        "pushName": "Fulano",
        "message": {"conversation": "🚛 Veículos Online"}
      },
      "instance": "minha-instancia"
    },
    "event": "messages.upsert",
    "date_time": "2026-10-08T12:00:00Z"
  }'
```

O estado da conversa fica na tabela `t_pbi_interacoes_chatbot`, com as colunas
`chat_id`, `nome`, `ja_se_apresentou`, `encerrado`, `aviso_enviado`,
`ultima_interacao` e `count_bloqueio`.

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

25 testes cobrem a interpretação dos comandos, a autorização por número, todos
os caminhos da máquina de estados, a parametrização do SQL e o endpoint de
ponta a ponta (token, primeiro contato, bloqueio e banco indisponível). O banco
é um dublê em memória que registra cada `execute`, então nada exige SQL Server.
O CI roda a suíte a cada push.

## Próximos passos

- Envio real pela Evolution API (hoje `external_api_service` só registra).
- Textos de apresentação, menu e comando inválido.
- Consultas de telemetria por trás de cada comando (frota online, motor ligado
  parado, desempenho, abastecimentos, jornada e localização por placa).
