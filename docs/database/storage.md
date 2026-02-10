# Supabase Storage

## Bucket

- Nome: `whatsapp_media`
- Uso: armazenamento de fotos enviadas no fluxo de doacao

## Estrutura de paths

- `temp/YYYY-MM/arquivo.ext`

## Permissoes

- Upload: usando chave de servico no backend
- Leitura: URL publica (ou politica equivalente)

## Boas praticas

- Definir politica de retencao operacional
- Limpar prefixos antigos para economizar espaco no plano free
