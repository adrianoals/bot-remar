# Documentacao do Projeto Remar

Esta pasta contem a documentacao oficial da implementacao Python do chatbot Remar.

## Estrutura

- `context/ChatRemar.json`: workflow original no n8n (referencia historica e funcional).
- `context/README.md`: como usar o JSON de referencia.
- `architecture.md`: arquitetura da aplicacao atual.
- `flows.md`: estados e fluxos conversacionais implementados.
- `integrations.md`: MegaAPI, Supabase e Google Sheets.
- `deploy.md`: guia de deploy em producao.
- `deploy-checklist.md`: status do deploy atual (o que ja foi feito e pendencias).
- `operations.md`: operacao, limpeza e troubleshooting.
- `database/README.md`: schema e uso do banco.
- `database/database.sql`: schema completo recomendado.
- `database/add_mensagem_temp_column.sql`: migracao incremental.
- `database/storage.md`: configuracao do bucket de midia.

## Escopo atual

- Implementacao principal em Python/FastAPI.
- Banco em Supabase (Postgres + Storage).
- Google Sheets opcional para registro de leads e doacoes.
- n8n mantido apenas como referencia.
