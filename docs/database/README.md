# Banco de Dados

## Arquivos

- `database.sql`: schema completo recomendado.
- `add_mensagem_temp_column.sql`: migracao incremental para ambientes antigos.
- `add_automacao_controle.sql`: cria controle global de automacao (painel/comandos).
- `storage.md`: configuracao do bucket de midia.

## Tabelas

- `conversas`
  - controle de estado e dados temporarios (`mensagem_temp`)
- `doacoes`
  - dados finais do fluxo de doacao de item
- `automacao_controle`
  - controle global de automacao (`ativo_global`)

## Campos chave em `doacoes`

- `tipo_doacao`
- `estado_doacao`
- `nome_responsavel`
- `endereco_retirada`
- `telefone_whatsapp`
- `email`
- `horario_preferencial`
- `fotos`

## Observacao

`fotos` pode armazenar JSON string com multiplas URLs quando a coluna estiver como `TEXT`.
