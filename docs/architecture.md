# Arquitetura Atual

## Stack

- Python + FastAPI (`app/main.py`)
- Webhook da MegaAPI (`/megaapi`)
- Supabase (tabelas `conversas`, `doacoes`, Storage `whatsapp_media`)
- Google Sheets (opcional)

## Fluxo de alto nivel

1. MegaAPI envia webhook para `/megaapi`.
2. Aplicacao valida evento (ignora `ack`, grupos e mensagens proprias).
3. Extrai `wa_id`/`senderPn` e busca estado em `conversas`.
4. Processa o fluxo por estado.
5. Atualiza estado/dados no Supabase.
6. Envia resposta pela MegaAPI.
7. Em eventos finais, registra no Google Sheets (se configurado).

## Identificacao de usuario

- Destino de resposta prioriza `senderPn`.
- Chave de conversa no banco tambem prioriza `senderPn` normalizado.

## Midia

- Download via MegaAPI.
- Extracao de bytes reais da resposta (inclusive quando vem JSON/base64/url).
- Upload no Supabase Storage em `temp/YYYY-MM/`.
- URLs salvas em `doacoes.fotos`.
