# Remar Chatbot — WhatsApp Chatbot for Associação Remar do Brasil

🇧🇷 [Leia em Português](README.pt-br.md)

Built for **Associação Remar do Brasil** by **XNAP**

A WhatsApp chatbot that automates donor engagement and social service inquiries for Associação Remar do Brasil. It manages multi-step conversational flows — from item donations with photo collection to shelter referrals — using a state-machine architecture powered by FastAPI and Supabase.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** FastAPI + Uvicorn
- **Database & Storage:** Supabase (Postgres + Storage)
- **WhatsApp Gateway:** MegaAPI
- **Configuration:** Pydantic Settings + python-dotenv
- **Optional Integration:** Google Sheets (logging completed flows)
- **Infrastructure:** Docker Compose, GitHub Actions CI/CD

## Features

- **State-machine conversation engine** — each user progresses through defined states stored in Supabase, enabling multi-step flows with data collection and validation
- **Item donation flow** — 9-step guided process collecting category, condition, contact info, preferred pickup time, and photos
- **Service directory** — quick-access flows for shelters (acolhimento), solidarity shops, services, and freight/moving
- **Media handling** — downloads media from WhatsApp via MegaAPI, detects format by magic bytes, uploads to Supabase Storage
- **Admin panel** — web-based interface at `/admin` with global automation on/off toggle and per-user manual mode
- **Google Sheets logging** — optional integration that logs completed interactions to spreadsheet tabs by category
- **CI/CD pipeline** — automated tests on push, deploy to VPS via SSH on main branch

## Project Structure

```
Remar/
├── app/
│   ├── api/                  # Webhook endpoint and admin panel routes
│   ├── core/                 # Configuration (Pydantic Settings)
│   ├── flows/                # FlowManager — state machine logic
│   ├── services/             # MegaAPI, Supabase, Google Sheets clients
│   └── templates/messages/   # User-facing message templates (pt-BR)
├── tests/
│   ├── unit/                 # Flow logic tests with mocks
│   ├── contracts/            # Webhook payload validation
│   ├── integration/          # Live Supabase tests (opt-in)
│   └── fixtures/             # Reference payloads
├── docs/                     # Architecture, flows, deploy, and DB docs
├── scripts/                  # Interactive chat simulator, connection tests
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.12+
- A Supabase project with the schema from `docs/database/database.sql`
- A MegaAPI instance for WhatsApp connectivity
- (Optional) Google Cloud service account for Sheets integration

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/remar.git
cd remar

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Running

```bash
# Local development
uvicorn app.main:app --host 0.0.0.0 --port 8000

# With Docker
docker compose up -d --build

# Health check
curl http://localhost:8000/health
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/megaapi` | WhatsApp webhook (MegaAPI) |
| `GET` | `/admin` | Admin panel |

### Running Tests

```bash
# All tests (unit + contracts)
python -m unittest discover -s tests -p "test_*.py" -v

# Live integration tests (requires Supabase credentials)
RUN_LIVE_TESTS=1 python -m unittest discover -s tests/integration -p "test_*.py" -v
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MEGA_API_URL` | Yes | MegaAPI base URL |
| `MEGA_API_INSTANCE_KEY` | Yes | MegaAPI instance identifier |
| `MEGA_API_TOKEN` | Yes | MegaAPI authentication token |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase service role or anon key |
| `LOG_LEVEL` | Yes | Logging level (e.g. `INFO`) |
| `LOG_JSON` | Yes | Set to `1` for JSON log format |
| `ADMIN_USER` | Yes | Admin panel username |
| `ADMIN_PASSWORD` | Yes | Admin panel password |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | No | Google Sheets ID for logging |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | Path to service account JSON |

See `.env.example` for a complete template with placeholders.

## License

Internal project of Associação Remar do Brasil.

---

Built with AI-assisted development using [Claude Code](https://claude.ai/code)
