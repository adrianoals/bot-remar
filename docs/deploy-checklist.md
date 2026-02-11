# Deploy Checklist (Status Atual)

Atualizado em: **10 de fevereiro de 2026**

Este documento resume o que ja foi feito na VPS e o que ainda falta para o go-live completo.

## Ambiente e infraestrutura

- [x] VPS reinstalada (ambiente limpo)
- [x] Ubuntu atualizado (`apt update/upgrade`)
- [x] Timezone configurado (`America/Sao_Paulo`)
- [x] Docker instalado
- [x] Docker Compose plugin instalado
- [x] Firewall UFW ativo
- [x] Portas liberadas: `22`, `80`, `443`

## Repositorio e acesso

- [x] Chave SSH da VPS criada para GitHub
- [x] Deploy Key adicionada no repositorio privado
- [x] Clone do projeto em `/opt/remar`
- [x] `git pull` funcionando

## Aplicacao na VPS

- [x] `.env` criado a partir de `.env.example`
- [x] Container buildado com sucesso
- [x] Aplicacao em execucao via `docker compose`
- [x] Healthcheck interno OK (`GET /health`)
- [x] Logs funcionando
- [x] Runtime migrado para Python `3.12` no container

## DNS

- [x] Registro `A` configurado para `bot.sorteionovo.com.br`
- [x] Resolucao confirmada para o IP da VPS (`147.93.9.54`)

## CI/CD

- [x] Workflow criado em `.github/workflows/deploy.yml`
- [x] Secrets do GitHub Actions configurados:
  - [x] `VPS_HOST`
  - [x] `VPS_USER`
  - [x] `VPS_SSH_KEY`
  - [x] `APP_HEALTHCHECK_URL` (opcional)
- [x] Primeiro deploy automatico validado via push em `main`

## HTTPS e webhook (pendente para producao)

- [x] Configurar reverse proxy (recomendado: Nginx + Certbot)
- [x] Emitir certificado TLS para `bot.sorteionovo.com.br`
- [x] Validar acesso externo HTTPS
- [x] Configurar webhook da MegaAPI:
  - [x] URL: `https://bot.sorteionovo.com.br/megaapi`
  - [x] Metodo: `POST`

## Validacao funcional final

- [ ] Teste ponta a ponta no WhatsApp em producao
- [ ] Confirmar gravacao em `conversas` e `doacoes` no Supabase
- [ ] Confirmar upload de fotos no Supabase Storage
- [ ] Confirmar escrita na planilha Google (se habilitada)
- [ ] Revisar logs durante o fluxo real

## Comandos de verificacao rapida

```bash
cd /opt/remar
docker compose ps
curl -fsS http://127.0.0.1:8000/health
docker compose logs --tail=200 remar-bot
```

## Proximo passo recomendado

1. Configurar HTTPS (Nginx + Certbot).
2. Apontar webhook da MegaAPI.
3. Rodar teste real de mensagem.
