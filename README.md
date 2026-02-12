# Remar Chatbot

Chatbot de WhatsApp da **Associação Remar do Brasil**, implementado em Python/FastAPI, com lógica de atendimento por máquina de estados.

## Visão Geral

O bot atende fluxos de:

- Doação em valor
- Doação de itens (fluxo completo com coleta de dados e fotos)
- Acolhimento
- Lojas solidárias
- Serviços
- Fretes e mudanças

Persistência principal:

- Supabase Postgres (`conversas`, `doacoes`)
- Supabase Storage (`whatsapp_media`)
- Google Sheets (opcional)

Referência histórica de fluxo:

- `docs/context/ChatRemar.json` (workflow original no n8n)

## Stack

- Python 3.12+
- FastAPI + Uvicorn
- Supabase Python Client
- httpx
- pydantic-settings
- python-dotenv

## Estrutura

```text
Remar/
├── app/
│   ├── api/                 # Webhook e rotas
│   ├── core/                # Configurações
│   ├── flows/               # Fluxo conversacional
│   ├── services/            # MegaAPI, Supabase, Google Sheets
│   └── templates/           # Mensagens do bot
├── docs/                    # Documentação oficial do projeto
├── scripts/                 # Utilitários manuais
├── tests/
│   ├── unit/                # Testes de lógica com mocks
│   ├── contracts/           # Contratos de payload/eventos
│   ├── integration/         # Integração real (opcional/live)
│   └── fixtures/            # Payloads de referência
└── requirements.txt
```

## Configuração

1. Instale dependências:

```bash
pip install -r requirements.txt
```

2. Configure o `.env` (base em `.env.example`):

Obrigatórias:

- `MEGA_API_URL`
- `MEGA_API_INSTANCE_KEY`
- `MEGA_API_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `LOG_LEVEL` (ex.: `INFO`)
- `LOG_JSON` (`1` para JSON em produção)
- `ADMIN_USER` (painel `/admin`)
- `ADMIN_PASSWORD` (painel `/admin`)

Opcionais (Google Sheets):

- `GOOGLE_SHEETS_SPREADSHEET_ID`
- `GOOGLE_APPLICATION_CREDENTIALS` ou `GOOGLE_SHEETS_CREDENTIALS_JSON`

3. Garanta schema e storage no Supabase:

- `docs/database/database.sql`
- `docs/database/storage.md`

## Execução

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Webhook esperado:

- `POST /megaapi`

Saúde da aplicação:

- `GET /health`
- Painel administrativo: `GET /admin`

## Testes

Executar suíte automatizada (unit + contracts + integration opcional com skip):

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Executar integração real com Supabase:

```bash
RUN_LIVE_TESTS=1 python -m unittest discover -s tests/integration -p "test_*.py" -v
```

## Scripts Manuais

- `scripts/interactive_chat.py`: simulação interativa no terminal
- `scripts/test_supabase_connection.py`: smoke check manual de conexão com Supabase

## Documentação

Comece por:

- `docs/README.md`
- `docs/architecture.md`
- `docs/flows.md`
- `docs/integrations.md`
- `docs/deploy.md`
- `docs/operations.md`

## Observabilidade (produção)

- `docker-compose.yml` já inclui:
  - `healthcheck` em `/health`
  - rotação de logs (`max-size=10m`, `max-file=5`)
  - logs JSON (`LOG_JSON=1`)
- Para acompanhar em tempo real:

```bash
docker compose logs -f --tail=200
```

## CI/CD (GitHub Actions)

Workflow: `.github/workflows/deploy.yml`

Fluxo:

1. Executa testes automáticos.
2. Em `main`, conecta na VPS por SSH.
3. Roda `docker compose up -d --build --remove-orphans`.
4. Opcional: smoke test com URL de health.

Secrets esperados no GitHub:

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `APP_HEALTHCHECK_URL` (opcional, ex.: `https://bot.sorteionovo.com.br/health`)

## Licença

Projeto interno da Associação Remar do Brasil.
