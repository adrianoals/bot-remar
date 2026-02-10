# Deploy (Pos-Reinstalacao da VPS)

Este guia parte do cenario: VPS recem-reinstalada (Ubuntu 24.04), ambiente vazio, e deploy do bot em `bot.sorteionovo.com.br`.

## 1. Preparar servidor base

Conecte na VPS:

```bash
ssh root@SEU_IP
```

Atualize sistema e pacotes:

```bash
apt update && apt -y upgrade
apt -y autoremove && apt -y autoclean
timedatectl set-timezone America/Sao_Paulo
```

Instale utilitarios:

```bash
apt install -y ca-certificates curl gnupg ufw git
```

## 2. Instalar Docker + Compose plugin

```bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Validacao:

```bash
docker --version
docker compose version
```

## 3. Firewall (UFW)

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status
```

## 4. DNS do dominio

No painel DNS, crie/ajuste:

- tipo `A`
- host `bot`
- valor `IP_DA_VPS`
- TTL padrao

Dominio final esperado: `bot.sorteionovo.com.br`.

## 5. Subir codigo do projeto

Exemplo em `/opt/remar`:

```bash
mkdir -p /opt/remar
cd /opt/remar
git clone SEU_REPOSITORIO .
```

Crie o arquivo de ambiente:

```bash
cp .env.example .env
nano .env
```

Preencha obrigatorios:

- `MEGA_API_URL`
- `MEGA_API_INSTANCE_KEY`
- `MEGA_API_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `LOG_LEVEL` (recomendado `INFO`)
- `LOG_JSON` (recomendado `1`)

## 6. Storage e banco no Supabase

Antes do primeiro uso:

- Rode SQL de schema: `docs/database/database.sql`
- Configure bucket/politicas: `docs/database/storage.md`

## 7. Subir aplicacao com Docker Compose

No diretorio do projeto:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f --tail=200
```

O container deve expor a API em `:8000`.

## 8. HTTPS (obrigatorio para webhook)

Opcao recomendada: manter um reverse proxy (Traefik ou Nginx) terminando TLS e encaminhando para `127.0.0.1:8000`.

Requisito final:

- URL publica HTTPS ativa para o bot (ex.: `https://bot.sorteionovo.com.br`)
- endpoint do webhook: `POST /megaapi`

## 9. Configurar webhook na MegaAPI

Defina na MegaAPI:

- URL: `https://bot.sorteionovo.com.br/megaapi`
- metodo: `POST`

## 10. Checklist de validacao

- `GET /health` responde `200`
- chegada de mensagem de teste no WhatsApp
- fluxo de doacao de item completo
- grava em `conversas` e `doacoes` no Supabase
- salva foto no Storage com link publico
- (se habilitado) linha correta no Google Sheets

## 11. Operacao diaria

Ver logs:

```bash
cd /opt/remar
docker compose logs -f --tail=200
```

Atualizar versao:

```bash
cd /opt/remar
git pull
docker compose up -d --build
```

Checar saude:

```bash
curl -fsS http://127.0.0.1:8000/health
```

## 12. CI/CD automatico (GitHub Actions)

Arquivo no repositorio:

- `.github/workflows/deploy.yml`

Configure secrets no GitHub (`Settings > Secrets and variables > Actions`):

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `APP_HEALTHCHECK_URL` (opcional)

Fluxo:

1. Push em `main`
2. Executa testes
3. Copia codigo para `/opt/remar`
4. Rebuild/restart com Docker Compose
5. Smoke test no health (se configurado)

## 13. Rollback rapido

Se der problema apos update:

```bash
cd /opt/remar
git log --oneline -n 5
git checkout COMMIT_ANTERIOR
docker compose up -d --build
```

## 14. Observabilidade recomendada

- Healthcheck ativo no compose (`/health`)
- Logs estruturados (`LOG_JSON=1`)
- Rotacao de logs Docker (`10m x 5`)
- Monitor externo batendo em `https://bot.sorteionovo.com.br/health`
- Alertas por falha de healthcheck (Uptime Kuma, Better Stack ou similar)

## Observacoes

- Este projeto novo nao depende de n8n, Redis ou Postgres local.
- O banco oficial do bot e o Supabase.
- Para volume atual baixo, uma unica instancia da API atende bem.
