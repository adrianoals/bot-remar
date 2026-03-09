# Remar Chatbot — Chatbot de WhatsApp para a Associação Remar do Brasil

🇺🇸 [Read in English](README.md)

Desenvolvido para a **Associação Remar do Brasil** por **XNAP**

Chatbot de WhatsApp que automatiza o engajamento de doadores e consultas de serviços sociais da Associação Remar do Brasil. Gerencia fluxos conversacionais de múltiplas etapas — desde doações de itens com coleta de fotos até encaminhamentos para acolhimento — usando uma arquitetura de máquina de estados com FastAPI e Supabase.

## Stack Tecnológica

- **Linguagem:** Python 3.12
- **Framework:** FastAPI + Uvicorn
- **Banco de Dados e Storage:** Supabase (Postgres + Storage)
- **Gateway WhatsApp:** MegaAPI
- **Configuração:** Pydantic Settings + python-dotenv
- **Integração Opcional:** Google Sheets (registro de fluxos concluídos)
- **Infraestrutura:** Docker Compose, GitHub Actions CI/CD

## Funcionalidades

- **Motor conversacional com máquina de estados** — cada usuário progride através de estados definidos armazenados no Supabase, permitindo fluxos de múltiplas etapas com coleta e validação de dados
- **Fluxo de doação de itens** — processo guiado de 9 etapas coletando categoria, condição, dados de contato, horário preferencial de retirada e fotos
- **Diretório de serviços** — fluxos de acesso rápido para acolhimento, lojas solidárias, serviços e fretes/mudanças
- **Tratamento de mídia** — baixa mídia do WhatsApp via MegaAPI, detecta formato por magic bytes, faz upload para o Supabase Storage
- **Painel administrativo** — interface web em `/admin` com controle global de automação (liga/desliga) e modo manual por usuário
- **Registro no Google Sheets** — integração opcional que registra interações concluídas em abas da planilha por categoria
- **Pipeline CI/CD** — testes automatizados a cada push, deploy na VPS via SSH na branch main

## Estrutura do Projeto

```
Remar/
├── app/
│   ├── api/                  # Endpoint do webhook e rotas do painel admin
│   ├── core/                 # Configuração (Pydantic Settings)
│   ├── flows/                # FlowManager — lógica da máquina de estados
│   ├── services/             # Clientes MegaAPI, Supabase, Google Sheets
│   └── templates/messages/   # Templates de mensagens (pt-BR)
├── tests/
│   ├── unit/                 # Testes de lógica de fluxo com mocks
│   ├── contracts/            # Validação de payloads do webhook
│   ├── integration/          # Testes com Supabase real (opt-in)
│   └── fixtures/             # Payloads de referência
├── docs/                     # Arquitetura, fluxos, deploy e documentação do BD
├── scripts/                  # Simulador de chat interativo, testes de conexão
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Primeiros Passos

### Pré-requisitos

- Python 3.12+
- Um projeto Supabase com o schema de `docs/database/database.sql`
- Uma instância MegaAPI para conectividade com WhatsApp
- (Opcional) Conta de serviço Google Cloud para integração com Sheets

### Instalação

```bash
# Clonar o repositório
git clone https://github.com/your-org/remar.git
cd remar

# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

### Execução

```bash
# Desenvolvimento local
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Com Docker
docker compose up -d --build

# Verificação de saúde
curl http://localhost:8000/health
```

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Verificação de saúde do serviço |
| `POST` | `/megaapi` | Webhook do WhatsApp (MegaAPI) |
| `GET` | `/admin` | Painel administrativo |

### Executando Testes

```bash
# Todos os testes (unit + contracts)
python -m unittest discover -s tests -p "test_*.py" -v

# Testes de integração ao vivo (requer credenciais do Supabase)
RUN_LIVE_TESTS=1 python -m unittest discover -s tests/integration -p "test_*.py" -v
```

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `MEGA_API_URL` | Sim | URL base da MegaAPI |
| `MEGA_API_INSTANCE_KEY` | Sim | Identificador da instância MegaAPI |
| `MEGA_API_TOKEN` | Sim | Token de autenticação da MegaAPI |
| `SUPABASE_URL` | Sim | URL do projeto Supabase |
| `SUPABASE_KEY` | Sim | Chave service role ou anon do Supabase |
| `LOG_LEVEL` | Sim | Nível de log (ex.: `INFO`) |
| `LOG_JSON` | Sim | Definir `1` para formato de log JSON |
| `ADMIN_USER` | Sim | Usuário do painel administrativo |
| `ADMIN_PASSWORD` | Sim | Senha do painel administrativo |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | Não | ID da planilha Google Sheets para registro |
| `GOOGLE_APPLICATION_CREDENTIALS` | Não | Caminho para o JSON da conta de serviço |

Veja `.env.example` para um template completo com placeholders.

## Licença

Projeto interno da Associação Remar do Brasil.

---

Desenvolvido com desenvolvimento assistido por IA usando [Claude Code](https://claude.ai/code)
