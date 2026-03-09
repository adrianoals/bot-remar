# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Remar Chatbot is a WhatsApp chatbot for Associação Remar do Brasil, built with Python 3.12 and FastAPI. It manages conversational flows for item donations, social services, and community support through a state-machine architecture. Messages are received/sent via MegaAPI (WhatsApp gateway), state is stored in Supabase, and media files are uploaded to Supabase Storage.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run a single test file
python -m unittest tests/unit/test_flow_manager.py -v

# Run live integration tests (requires real Supabase credentials)
RUN_LIVE_TESTS=1 python -m unittest discover -s tests/integration -p "test_*.py" -v

# Docker
docker compose up -d --build
docker compose logs -f --tail=200

# Health check
curl http://127.0.0.1:8000/health
```

## Architecture

**State Machine Pattern:** The core logic lives in `app/flows/manager.py` (FlowManager). Each user has a current state stored in the `conversas` Supabase table. On each incoming message, the FlowManager loads the user's state, routes to the appropriate handler, updates state/data, and sends a response.

**Key states:** `inicio` (main menu) → branching into `doacao` (9-step donation flow), `acolhimento`, `lojas`, `servico`, `fretes`, or `manual` (human takeover).

**Request lifecycle:**
1. MegaAPI sends webhook to `POST /megaapi`
2. `app/api/webhook.py` extracts wa_id and message content, validates (ignores own messages, groups, ACKs)
3. Checks global automation toggle and per-user automation status
4. FlowManager processes message based on current state
5. Response sent back via MegaAPI, state updated in Supabase

**Services layer** (`app/services/`):
- `mega_api.py` — WhatsApp messaging (send text, download/upload media, format detection via magic bytes)
- `supabase_service.py` — All database operations (user state, donations, media storage, automation control)
- `google_sheets_service.py` — Optional logging of completed flows to Google Sheets

**Message templates** in `app/templates/messages/` define all user-facing text, organized by flow (welcome, donation, services, etc.).

**Admin panel** (`app/api/admin.py`): Simple HTML-based interface at `/admin` with cookie auth for toggling global automation on/off.

## Database (Supabase)

Three tables: `conversas` (conversation state, keyed by wa_id), `doacoes` (donation records), `automacao_controle` (global automation toggle, single row with id=1). Schema in `docs/database/database.sql`. Media stored in `whatsapp_media` bucket under `temp/YYYY-MM/` path.

## Configuration

All config via environment variables, managed through `app/core/config.py` (Pydantic Settings). See `.env.example` for required variables. Key groups: MegaAPI credentials, Supabase credentials, optional Google Sheets credentials, admin panel credentials.

## Deployment

Production runs on a VPS (Ubuntu 24.04) via Docker Compose. CI/CD through GitHub Actions (`.github/workflows/deploy.yml`): tests run on push, deploy to VPS via SSH on main branch. Domain: bot.sorteionovo.com.br.

## Language

All user-facing messages and variable names are in Brazilian Portuguese. Code comments and documentation may mix Portuguese and English.
