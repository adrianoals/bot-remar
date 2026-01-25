# Google Sheets — Análise e Plano de Implementação

**Data:** 2025-01-25  
**Referência n8n:** `docs/context/ChatRemar.json`

---

## 1. Existe integração? **NÃO**

No projeto Python **não há** nenhuma integração com Google Sheets.

### Onde procurei

| Local | Resultado |
|-------|-----------|
| `app/` (código) | Nenhuma menção a `google`, `sheets`, `gspread`, `googleapis` |
| `requirements.txt` | Nenhuma dependência (`gspread`, `google-auth`, `google-api-python-client`) |
| `.env` / `.env.example` | Nenhuma variável `GOOGLE_*`, `SHEET_*`, `SPREADSHEET_*` |
| `app/services/` | Só `mega_api.py` e `supabase_service.py` |
| `app/flows/manager.py` | Nenhuma chamada a planilha |
| `app/core/config.py` | Não verificado; tende a não ter config de Google |

A documentação (`docs/RESUMO_IMPLEMENTACAO.md`, `docs/IMPLEMENTACAO_COMPLETA.md`, `docs/ANALISE_COMPARATIVA.md`) já indica que a integração com Google Sheets **não foi implementada** e que não é crítica para o bot.

---

## 2. Onde está implementada no projeto? — **N/A**

Não existe implementação. Os únicos pontos que citam Sheets são os `.md` em `docs/`.

---

## 3. Como é acionada? — **N/A**

---

## 4. Que dados ela lê/escreve? — **Conforme n8n (a replicar)**

Com base no n8n, os dados que **devem** ser escritos no Google Sheets são os descritos nas seções 7 e 8 adiante.

---

## 5. Status da integração

| Status | Descrição |
|--------|-----------|
| **Inexistente** | Nenhum serviço, config, env ou chamada relacionada a Google Sheets. |

---

## 6. O que o n8n faz (resumo)

No `ChatRemar.json` existem **6 nós** `n8n-nodes-base.googleSheets`:

| Nó n8n | Operação | Planilha (documentId) | Aba (sheetName) | Quando é acionado (fluxo resumido) |
|--------|----------|------------------------|-----------------|-------------------------------------|
| **Google Sheets** | `append` | `1oqLXetRi9Z_yBj0LUFkUZU9g6yCigGDgxec9tU5VOjI` | Doação Valor (gid 1506373255) | Doação em valor: Supabase4 → HTTP Request12 → Edit Fields1 → **Google Sheets** |
| **Google Sheets1** | `append` | idem | Acolhimento (gid 84924559) | Acolhimento opção 1: Supabase14 → HTTP Request22 → Edit Fields4 → **Google Sheets1** |
| **Google Sheets2** | `append` | idem | Lojas Solidárias (gid 212322705) | Lojas opção 1: Supabase15 → HTTP Request18 → Edit Fields5 → **Google Sheets2** |
| **Google Sheets3** | `append` | idem | Contratar Um Serviço (gid 1419884578) | Serviços opção 1: Supabase20 → HTTP Request28 → Edit Fields6 → **Google Sheets3** |
| **Google Sheets4** | `append` | idem | Fretes e Mudanças (gid 578078654) | Fretes opção 1: Supabase22 → HTTP Request30 → Edit Fields8 → **Google Sheets4** |
| **Google Sheets5** | `append` | idem | Doação Item (gid 0) | Doação item finalizada: HTTP Request75 → Edit Fields11 → **Google Sheets5** |

- **Autenticação n8n:** `googleSheetsOAuth2Api` (credencial "Google Sheets Remar").
- **Operação:** só `append`; não há `read`, `update`, `batchUpdate`, etc.
- **Erro:** os nós Google Sheets no JSON não têm `retryOnFail` nem `onError`; em caso de falha, o fluxo n8n para.

---

## 7. Estrutura/aba/colunas por planilha

Todas usam o mesmo **documentId** (planilha "REMAR CHAT") e apenas **abas** diferentes.

### 7.1 Doação Valor (gid 1506373255)

| Coluna | Origem (n8n) | Origem no Python |
|--------|--------------|------------------|
| Data de Contato | `Supabase4.data` (pt-BR) | `conversas.data` (formatar `DD/MM/YYYY`) |
| Horário de Contato | `Supabase4.horario` | `conversas.horario` |
| Telefone de Contato | `Supabase4.wa_id` | `conversas.wa_id` |
| Nome do Contato | `Infos Manuais.nome` | `conversas.nome` |
| Doação Valor | `"-"` (fixo) | `"-"` |

### 7.2 Acolhimento (gid 84924559)

| Coluna | Valor / origem |
|--------|----------------|
| Data de Contato | `conversas.data` (pt-BR) |
| Horário de Contato | `conversas.horario` |
| Telefone de Contato | `conversas.wa_id` |
| Nome do Contato | `conversas.nome` |
| Acolhimento | `"Aguardando Acolhimento"` (fixo) |

### 7.3 Lojas Solidárias (gid 212322705)

| Coluna | Valor / origem |
|--------|----------------|
| Data de Contato | `conversas.data` (pt-BR) |
| Horário de Contato | `conversas.horario` |
| Telefone de Contato | `conversas.wa_id` |
| Nome do Contato | `conversas.nome` |
| Lojas Solidárias | `"Contato para Lojas Soidárias"` (fixo; typo do n8n) |

### 7.4 Contratar Um Serviço (gid 1419884578)

| Coluna | Valor / origem |
|--------|----------------|
| Data de Contato | `conversas.data` (pt-BR) |
| Horário de Contato | `conversas.horario` |
| Telefone de Contato | `conversas.wa_id` |
| Nome do Contato | `conversas.nome` |
| Contratar um Serviço | `"Contato Para Serviço"` (fixo) |

### 7.5 Fretes e Mudanças (gid 578078654)

| Coluna | Valor / origem |
|--------|----------------|
| Data de Contato | `conversas.data` (pt-BR) |
| Horário de Contato | `conversas.horario` |
| Telefone de Contato | `conversas.wa_id` |
| Nome do Contato | `conversas.nome` |
| Frees e Mudanças | `"Contato Para Fretes e Mudanças"` (fixo; n8n usa "Frees") |

### 7.6 Doação Item (gid 0)

| Coluna | Origem (n8n) | Origem no Python |
|--------|--------------|------------------|
| Email | `$json.email` (doação) | `doacao["email"]` |
| Nome | `$json.nome` | `doacao["nome_responsavel"]` |
| Telefone | `$json.telefone` | `doacao["telefone_whatsapp"]` |
| Endereço | `$json['Endereço']` | `doacao["endereco_retirada"]` |
| Tipo De Doação | `$json.tipo_doacao` | `doacao["tipo_doacao"]` |
| Estado Doação | `$json.estado_doacao` | `doacao["estado_doacao"]` |
| Horário Preferencial | `$json.horario_preferencial` | `doacao["horario_preferencial"]` |
| Fotos | `$json.fotos` | `doacao["fotos"]` (lista → string: `"\n".join` ou `", ".join`) |
| Verificar Foto | `"Copie a URL"` (fixo) | `"Copie a URL"` |
| Data Criação | `new Date().toLocaleDateString('en-GB'...).replace(/\//g, '-')` | `datetime.now().strftime("%d-%m-%Y")` |
| Horário | `new Date().toLocaleString('pt-BR'...).split(' ')[1]` | `datetime.now().strftime("%H:%M:%S")` ou `"%H:%M"` |

---

## 8. Itens a implementar (checklist)

### 8.1 Autenticação

| # | Item | Detalhe |
|---|------|---------|
| 1 | **Definir método de autenticação** | n8n usa **OAuth2** (`googleSheetsOAuth2Api`). Em Python é mais simples usar **Service Account**: criar no Google Cloud, baixar JSON, compartilhar a planilha "REMAR CHAT" com o email da service account (ex.: `xxx@yyy.iam.gserviceaccount.com`). |
| 2 | **Credenciais Service Account** | Arquivo JSON (não versionar). Ou variáveis: `GOOGLE_SHEETS_CREDENTIALS_JSON` (JSON string) ou `GOOGLE_APPLICATION_CREDENTIALS` (caminho do arquivo). |
| 3 | **(Opcional) OAuth2** | Se quiser paridade total com n8n: fluxo OAuth, armazenar/renovar tokens (ex. em DB ou arquivo). Maior esforço. |

### 8.2 Leitura/escrita

| # | Item | Detalhe |
|---|------|---------|
| 4 | **Append (append)** | Implementar **apenas append** de linhas. n8n não usa read, update, batchUpdate, clear. |
| 5 | **Formato de append** | Uma linha por evento; colunas na ordem das tabelas da seção 7. Usar API `spreadsheets.values.append` (range `NomeDaAba!A:Z` ou similar). |

### 8.3 Estrutura / abas

| # | Item | Detalhe |
|---|------|---------|
| 6 | **Document ID** | Configurável (ex. `GOOGLE_SHEETS_SPREADSHEET_ID`). Valor n8n: `1oqLXetRi9Z_yBj0LUFkUZU9g6yCigGDgxec9tU5VOjI`. |
| 7 | **Mapa de abas** | Mapear "tipo de evento" → nome da aba (ou gid): Doação Valor, Acolhimento, Lojas Solidárias, Contratar Um Serviço, Fretes e Mudanças, Doação Item. n8n usa gids; a API aceita nome da aba ou `Aba!A:K`. |
| 8 | **Cabeçalhos** | Garantir que as abas já tenham a primeira linha com os nomes das colunas (como no n8n); o append vai na próxima linha. |

### 8.4 Transformação/mapeamento

| # | Item | Detalhe |
|---|------|---------|
| 9 | **Conversas → Data/Horário** | `conversas.data` (date) → string `DD/MM/YYYY`. `conversas.horario` (time) → string `HH:MM` ou `HH:MM:SS`. Se `data`/`horario` forem nulos, usar `datetime.now()` em timezone `America/Sao_Paulo`. |
| 10 | **Doação → Doação Item** | Mapear `doacoes` (nome_responsavel, endereco_retirada, telefone_whatsapp, email, tipo_doacao, estado_doacao, horario_preferencial, fotos) para as colunas da aba Doação Item. |
| 11 | **Fotos** | `doacoes.fotos` pode ser lista de URLs.Converter para string (ex. `"\n".join(fotos)` se list, ou valor direto se já for string). |
| 12 | **Valores fixos** | Replicar literais: `"-"`, `"Aguardando Acolhimento"`, `"Contato para Lojas Soidárias"`, `"Contato Para Serviço"`, `"Contato Para Fretes e Mudanças"`, `"Copie a URL"`. |

### 8.5 Validações e tratamento de erros

| # | Item | Detalhe |
|---|------|---------|
| 13 | **Validação antes de append** | Garantir que `wa_id`/`conversas` ou `doacao` existam quando for escrever. Evitar append com dados críticos vazios se fizer sentido (ex. nome/telefone para contato). |
| 14 | **Tratamento de erros** | Capturar exceções da API (quota, rede, 403, 404). **Não** interromper o fluxo do bot: logar e seguir (equivalente a `onError: continue`). |
| 15 | **Timeout / retries** | Definir timeout (ex. 10s) e opcionalmente 1–2 retries com backoff; em falha, apenas log. |

### 8.6 Logs e reprocessamento

| # | Item | Detalhe |
|---|------|---------|
| 16 | **Logs** | Logar: sucesso (tipo de evento, aba, wa_id), falha (mensagem, tipo, wa_id). Não logar dados sensíveis (ex. email em nível INFO). |
| 17 | **Reprocessamento** | n8n não tem fila de reprocessamento para Sheets. Opcional: em caso de falha, gravar em tabela/fila (Supabase, Redis, etc.) para reprocesso posterior. Não obrigatório para paridade. |

---

## 9. Onde implementar no projeto

### 9.1 Novo serviço: `app/services/google_sheets_service.py`

- Classe `GoogleSheetsService`:
  - `__init__`: carrega credenciais (Service Account) e `SPREADSHEET_ID`.
  - `append_doacao_valor(conversas_row: dict)`
  - `append_acolhimento(conversas_row: dict)`
  - `append_lojas(conversas_row: dict)`
  - `append_servico(conversas_row: dict)`
  - `append_fretes(conversas_row: dict)`
  - `append_doacao_item(doacao: dict)`
- Ou um método genérico: `_append(sheet_name: str, values: list)` e funções de mapeamento que montam `values` a partir de `conversas` ou `doacao`.
- Tratamento de erros e logs dentro do serviço.

### 9.2 Config: `app/core/config.py`

- `GOOGLE_SHEETS_SPREADSHEET_ID: str | None`
- `GOOGLE_APPLICATION_CREDENTIALS: str | None` (caminho) **ou** leitura de JSON embutido via `GOOGLE_SHEETS_CREDENTIALS_JSON` (ou outro nome), se preferir.

### 9.3 `app/flows/manager.py` — pontos de acionamento

Chamadas **não bloqueantes** (fire‑and‑forget ou `asyncio.create_task`), após enviar a mensagem e atualizar estado, para não atrasar a resposta ao usuário:

| Fluxo | Handler | Momento exato |
|-------|---------|---------------|
| Doação valor | `handle_doacao_tipo` | Após `send_text(DONATION_VALUE_MESSAGE)` e `update_state(wa_id, "reset")`. Buscar `conversas` (data, horario, wa_id, nome) e chamar `sheets.append_doacao_valor(...)`. |
| Acolhimento 1 | `handle_acolhimento` | Após `send_text(ACOLHIMENTO_CONTACT)` e `update_state(wa_id, "reset")`. Buscar `conversas` → `append_acolhimento`. |
| Lojas 1 | `handle_lojas` | Após `send_text(LOJAS_CONTACT)` e `update_state(wa_id, "reset")`. Buscar `conversas` → `append_lojas`. |
| Serviços 1 | `handle_servicos` | Após `send_text(SERVICES_CONTACT)` e `update_state(wa_id, "reset")`. Buscar `conversas` → `append_servico`. |
| Fretes 1 | `handle_fretes` | Após `send_text(FRETES_CONTACT)` e `update_state(wa_id, "reset")`. Buscar `conversas` → `append_fretes`. |
| Doação item finalizada | `handle_doacao_item` (estado 9, `text_content == "2"`) | Após `send_text(DONATION_CONFIRMATION)` e `update_state(wa_id, "reset")`. Buscar `get_latest_doacao(wa_id)` → `append_doacao_item`. |

Em todos: se `GoogleSheetsService` não estiver configurado (ex. `SPREADSHEET_ID` vazio), não chamar e não falhar.

### 9.4 Injeção no `FlowManager`

- Em `FlowManager.__init__`: instanciar `GoogleSheetsService` (ou None se config ausente) e guardar em `self.sheets` (ou similar).
- Nos handlers, chamar `self.sheets.append_*` quando aplicável.

### 9.5 Dependências

- `requirements.txt`:  
  - `google-auth`  
  - `google-api-python-client`  
  (ou `gspread`, que já usa essas por baixo; para `values.append`, `google-api-python-client` é suficiente.)

---

## 10. Configuração (env / segredos)

Não incluir credenciais reais em código ou em `.env` versionado.

### 10.1 Variáveis de ambiente sugeridas

```env
# Google Sheets (opcional; se vazias, a integração não é usada)
GOOGLE_SHEETS_SPREADSHEET_ID=1oqLXetRi9Z_yBj0LUFkUZU9g6yCigGDgxec9tU5VOjI
# Uma das duas:
GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/service-account.json
# OU (JSON string, útil em PaaS):
# GOOGLE_SHEETS_CREDENTIALS_JSON={"type":"service_account",...}
```

### 10.2 `.env.example`

Incluir apenas as chaves, com placeholders:

```env
GOOGLE_SHEETS_SPREADSHEET_ID=
GOOGLE_APPLICATION_CREDENTIALS=
```

### 10.3 Service Account

1. Google Cloud Console → IAM & Admin → Service Accounts → Create.
2. Criar chave JSON e guardar em local seguro.
3. Abrir a planilha "REMAR CHAT" e **Compartilhar** (Editor ou pelo menos “ pode editar”) com o email da service account.

### 10.4 IDs de aba (gids)

Se for usar ranges por nome de aba (recomendado para clareza), os nomes no n8n são:  
`Doação Valor`, `Acolhimento`, `Lojas Solidárias`, `Contratar Um Serviço`, `Fretes e Mudanças`, `Doação Item`.  
Se a API for usada com gid, os valores estão na seção 7.

---

## 11. Resumo do checklist de implementação

| # | Item | Onde | Prioridade |
|---|------|------|------------|
| 1 | Autenticação (Service Account ou OAuth) | `google_sheets_service.py`, `config` | Alta |
| 2 | Variáveis de ambiente e carregamento | `config.py`, `.env.example` | Alta |
| 3 | `GoogleSheetsService` + `append` por aba | `app/services/google_sheets_service.py` | Alta |
| 4 | Mapeamento conversas → 5 abas (valor, acolhimento, lojas, serviço, fretes) | Dentro do serviço | Alta |
| 5 | Mapeamento doacao → aba Doação Item | Dentro do serviço | Alta |
| 6 | Formatação data/hora (pt-BR, America/Sao_Paulo) | Serviço ou helpers | Média |
| 7 | Tratamento de erros e logs (não quebrar o fluxo) | Serviço + `manager` (try/except ao chamar) | Alta |
| 8 | Chamadas no `manager` nos 6 momentos descritos | `app/flows/manager.py` | Alta |
| 9 | Inicialização condicional (se config não presente, não instanciar) | `FlowManager.__init__` | Média |
| 10 | `google-auth` e `google-api-python-client` em `requirements.txt` | `requirements.txt` | Alta |
| 11 | (Opcional) Retries/timeout | `google_sheets_service.py` | Baixa |
| 12 | (Opcional) Fila de reprocesso em falha | Nova tabela ou job assíncrono | Baixa |

---

## 12. Observações finais

- A integração no n8n é **só append**; não há leitura nem alteração de células.
- O n8n usa **OAuth2**; em Python, **Service Account** reduz bastante a complexidade, desde que a planilha seja compartilhada.
- O `documentId` no JSON do n8n é um ID real. Em produção, convém usar um ID configurável (ex. outra planilha de homologação).
- Mantendo as strings fixas exatamente iguais às do n8n (“Contato para Lojas Soidárias”, “Frees e Mudanças”) preserva compatibilidade com eventual uso já existente desses rótulos em outras partes do processo.
