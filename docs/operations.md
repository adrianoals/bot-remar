# Operacao e Manutencao

## Limpeza de midia

Como os arquivos ficam em `temp/YYYY-MM/`, a limpeza pode ser mensal.

Exemplo de politica operacional:

- manter 1 ou 2 meses recentes
- remover prefixos antigos periodicamente

## Troubleshooting rapido

### Mensagens duplicadas ou eventos de confirmacao

- Eventos `message.ack` sao ignorados por regra.

### Midia nao abre no link

- Verificar logs `MEDIA DEBUG`:
  - `mimetype`
  - `ext_detected`
  - `content_type`
  - `signature`
- Validar se download retornou bytes reais e nao JSON sem dados de midia.

### Dados nao aparecem na planilha

- Conferir credenciais Google.
- Conferir `GOOGLE_SHEETS_SPREADSHEET_ID`.
- Conferir permissao de editor da service account na planilha.

## Escalabilidade (curto prazo)

Para crescimento moderado:

- manter app stateless
- adicionar idempotencia por `message_id`
- revisar chamadas bloqueantes para async real
