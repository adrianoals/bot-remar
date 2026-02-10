# Integracoes

## MegaAPI

- Recebe webhooks de mensagens.
- Envia respostas de texto.
- Faz download de midia por `downloadMediaMessage`.

### Ponto importante

A resposta de download pode vir em binario direto ou envelope JSON com base64/url. O servico trata os dois casos para obter bytes reais da midia.

## Supabase

- `conversas`: estado e dados temporarios.
- `doacoes`: dados consolidados do fluxo de doacao.
- Storage `whatsapp_media`: arquivos de midia.

### Organizacao dos arquivos no bucket

- Prefixo mensal: `temp/YYYY-MM/arquivo.ext`
- Objetivo: facilitar limpeza e reduzir acoplamento com identificador de usuario.

## Google Sheets (opcional)

Abas suportadas:

- Doacao Valor
- Acolhimento
- Lojas Solidarias
- Contratar Um Servico
- Fretes e Mudancas
- Doacao Item

A ordem de colunas em `Doacao Item` foi alinhada ao fluxo de referencia.
