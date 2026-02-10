# Deploy

## Requisitos

- Python 3.10+
- Variaveis de ambiente configuradas (`.env`)
- Supabase pronto (tabelas + bucket)
- Endpoint publico HTTPS para webhook

## Variaveis obrigatorias

- `MEGA_API_URL`
- `MEGA_API_INSTANCE_KEY`
- `MEGA_API_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_KEY`

## Subida local/producao

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Checklist de go-live

- Webhook configurado na MegaAPI para `POST /megaapi`
- Logs de aplicacao ativos
- Teste ponta a ponta: menu, doacao item, foto, finalizacao
- Verificacao de URL publica do Storage
