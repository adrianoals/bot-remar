# Configuração da Conta de Serviço (Google Sheets)

Este guia explica como criar uma **Service Account** no Google Cloud e configurá-la para a integração com o Google Sheets.

---

## 1. Acessar o Google Cloud Console

1. Abra: [https://console.cloud.google.com](https://console.cloud.google.com)
2. Faça login com a conta Google que tem acesso à planilha **REMAR CHAT** (ou que possa receber o compartilhamento depois).

---

## 2. Criar ou escolher um projeto

- **Novo projeto:** Menu (☰) → **IAM e administração** → **Gerenciar recursos** → **Criar projeto**  
  - Nome sugerido: `remar-chatbot` ou `remar-sheets`
- **Projeto existente:** Selecione-o no seletor de projetos (canto superior esquerdo).

---

## 3. Ativar a API Google Sheets

1. No menu: **APIs e serviços** → **Biblioteca** (ou [link direto](https://console.cloud.google.com/apis/library))
2. Procure por **Google Sheets API**
3. Clique e depois em **Ativar**

---

## 4. Criar a Conta de Serviço

1. **APIs e serviços** → **Credenciais**
2. Clique em **+ Criar credenciais** → **Conta de serviço**
3. Preencha:
   - **Nome da conta de serviço:** ex. `remar-sheets-bot`
   - **ID:** (gerado automaticamente; pode manter)
4. Clique em **Criar e continuar**
5. **Etapa 2 (opcional):** Conceder acesso ao projeto — pode pular → **Continuar**
6. **Etapa 3 (opcional):** Conceder acesso a usuários — pular → **Concluir**

---

## 5. Gerar a chave JSON

1. Na lista de **Contas de serviço**, clique na que você criou
2. Aba **Chaves** → **Adicionar chave** → **Criar nova chave**
3. Tipo: **JSON** → **Criar**
4. O arquivo será baixado (ex. `remar-chatbot-xxxxx.json`)

**Importante:**
- Guarde esse arquivo em local seguro e **nunca** envie para o Git
- O `.gitignore` já deve conter `*.json` em pastas de credenciais ou você pode colocar em `config/` ou na raiz com um nome como `google-service-account.json` e adicionar ao `.gitignore`

---

## 6. Copiar o e-mail da Conta de Serviço

Na tela da conta de serviço, no topo, aparece algo como:

```
remar-sheets-bot@remar-chatbot-123456.iam.gserviceaccount.com
```

Copie esse e-mail. Você vai usá-lo para **compartilhar a planilha**.

---

## 7. Compartilhar a planilha com a Service Account

1. Abra a planilha **REMAR CHAT** no Google Sheets:  
   [https://docs.google.com/spreadsheets/d/1oqLXetRi9Z_yBj0LUFkUZU9g6yCigGDgxec9tU5VOjI](https://docs.google.com/spreadsheets/d/1oqLXetRi9Z_yBj0LUFkUZU9g6yCigGDgxec9tU5VOjI)
2. Clique em **Compartilhar**
3. No campo "Adicionar pessoas e grupos", cole o **e-mail da conta de serviço** (ex. `remar-sheets-bot@remar-chatbot-xxxx.iam.gserviceaccount.com`)
4. Permissão: **Editor** (para poder adicionar linhas)
5. **Desmarque** "Notificar pessoas" (a conta de serviço não usa e-mail)
6. Clique em **Compartilhar** / **Enviar**

Sem esse passo, a API retornará erro de permissão ao fazer append.

---

## 8. Configurar o projeto Python

### Opção A: Arquivo JSON no disco (recomendado local)

1. Coloque o arquivo JSON em um local seguro, por exemplo:
   - `config/google-service-account.json`  
   - ou na raiz: `google-service-account.json`
2. Adicione ao `.gitignore` (se ainda não estiver):

   ```
   google-service-account.json
   config/google-service-account.json
   ```

3. No seu `.env`:

   ```env
   GOOGLE_SHEETS_SPREADSHEET_ID=1oqLXetRi9Z_yBj0LUFkUZU9g6yCigGDgxec9tU5VOjI
   GOOGLE_APPLICATION_CREDENTIALS=/caminho/absoluto/para/google-service-account.json
   ```

   No macOS/Linux, o caminho absoluto pode ser algo como:
   `/Users/adriano/Desktop/Remar/config/google-service-account.json`

### Opção B: JSON como variável de ambiente (útil em VPS/Docker)

Se preferir não ter o arquivo no servidor (ex. em PaaS):

1. Abra o JSON baixado e copie **todo** o conteúdo (um único bloco `{ ... }`)
2. No `.env`, em **uma única linha**, coloque (substitua `{...}` pelo JSON real):

   ```env
   GOOGLE_SHEETS_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...@....iam.gserviceaccount.com",...}
   ```

   Ou, em alguns ambientes, é mais fácil colocar o JSON em um arquivo e então, no host, fazer:
   `GOOGLE_SHEETS_CREDENTIALS_JSON=$(cat config/google-sa.json)` (evite versionar o arquivo).

O código verifica primeiro `GOOGLE_APPLICATION_CREDENTIALS` (caminho do arquivo) e, se não existir, usa `GOOGLE_SHEETS_CREDENTIALS_JSON`.

---

## 9. Verificar se está tudo certo

Se `GOOGLE_SHEETS_SPREADSHEET_ID` e uma das opções de credencial estiverem preenchidos, ao rodar o bot e disparar um dos fluxos que gravam no Sheets (doação valor, acolhimento, lojas, serviço, fretes ou finalização de doação de item), uma nova linha deve aparecer na aba correspondente.

Em caso de erro, confira:
- A planilha foi compartilhada com o **e-mail da conta de serviço** como **Editor**?
- A **Google Sheets API** está ativada no projeto?
- O caminho em `GOOGLE_APPLICATION_CREDENTIALS` está correto e o arquivo existe?
- O `GOOGLE_SHEETS_SPREADSHEET_ID` é o da planilha certa? (o ID está na URL: `/d/ID_AQUI/`)

---

## 10. Resumo rápido

| Etapa | Onde | O que fazer |
|-------|------|-------------|
| 1 | Google Cloud | Criar/escolher projeto |
| 2 | APIs e serviços → Biblioteca | Ativar **Google Sheets API** |
| 3 | Credenciais | Criar **Conta de serviço** |
| 4 | Conta de serviço → Chaves | Criar chave **JSON** e baixar |
| 5 | Google Sheets (REMAR CHAT) | **Compartilhar** com o e-mail da conta de serviço como **Editor** |
| 6 | Projeto | Colocar JSON em disco ou em `GOOGLE_SHEETS_CREDENTIALS_JSON` |
| 7 | `.env` | Definir `GOOGLE_SHEETS_SPREADSHEET_ID` e `GOOGLE_APPLICATION_CREDENTIALS` ou `GOOGLE_SHEETS_CREDENTIALS_JSON` |

Depois disso, a aplicação usa a Service Account automaticamente quando as variáveis estiverem configuradas.

---

## Referência

- Plano de implementação e mapeamento de abas/colunas: `docs/GOOGLE_SHEETS_ANALISE_E_PLANO.md`
