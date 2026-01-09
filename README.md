# Remar Chatbot

Chatbot para WhatsApp desenvolvido para a **Associação Remar do Brasil**, focado no atendimento automatizado ao público para doações e serviços assistenciais.

## Sobre o Projeto

O Remar Chatbot é um sistema de autoatendimento estruturado que opera como uma máquina de estados, permitindo que usuários interajam via WhatsApp para:

- **Fazer doações** (em valor ou itens físicos)
- **Solicitar acolhimento** e informações sobre programas de ressocialização
- **Conhecer as Lojas Solidárias** da associação
- **Contratar serviços** (reformas, pinturas, limpeza, etc.)
- **Solicitar fretes e mudanças**

O sistema gerencia o estado da conversa de cada usuário, permitindo que o bot lembre em que etapa o usuário parou e continue de onde parou.

## Tecnologias Utilizadas

### Backend
- **Python 3** - Linguagem de programação
- **FastAPI** - Framework web assíncrono para construção da API
- **Uvicorn** - Servidor ASGI para execução da aplicação

### Integrações
- **MegaAPI** - API para integração com WhatsApp (envio e recebimento de mensagens, mídia)
- **Supabase** - Banco de dados PostgreSQL gerenciado para armazenamento de estados de conversa e dados dos usuários

### Bibliotecas Python
- **pydantic-settings** - Gerenciamento de configurações e variáveis de ambiente
- **httpx** - Cliente HTTP assíncrono para requisições à MegaAPI
- **requests** - Cliente HTTP síncrono
- **python-dotenv** - Carregamento de variáveis de ambiente a partir de arquivos `.env`
- **supabase** - Cliente Python oficial do Supabase

### Arquitetura
- **Arquitetura baseada em regras** - Sistema de fluxo de conversação estruturado (não utiliza IA generativa)
- **Máquina de estados** - Gerenciamento de fluxo de conversação baseado em estados salvos no banco de dados
- **API REST** - Endpoints para recebimento de webhooks da MegaAPI

## Estrutura do Projeto

```
Remar/
├── app/
│   ├── api/              # Endpoints da API (webhooks)
│   ├── core/             # Configurações centrais
│   ├── flows/            # Gerenciamento de fluxos de conversação
│   ├── services/         # Serviços de integração (MegaAPI, Supabase)
│   └── templates/        # Templates de mensagens do WhatsApp
├── docs/                 # Documentação e arquivos de referência
└── requirements.txt      # Dependências do projeto
```

## Requisitos

- Python 3.8+
- Conta na MegaAPI com instância configurada
- Projeto no Supabase com tabelas configuradas
- Variáveis de ambiente configuradas (ver `.env.example`)

## Licença

Este projeto é propriedade da Associação Remar do Brasil.
