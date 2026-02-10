# Fluxos Conversacionais

## Estados principais

- `inicio`
- `doacao`
- `doacao_item_1` ... `doacao_item_9`
- `acolhimento`
- `lojas`
- `servico`
- `fretes`
- `reset`

## Menu principal

1. Fazer uma doacao
2. Quero acolhimento
3. Lojas solidarias
4. Contratar um servico
5. Fretes e mudancas

## Fluxo de doacao de item (resumo)

1. Categoria da doacao (`tipo_doacao`)
2. Estado dos itens (`estado_doacao` em texto)
3. Nome (com confirmacao)
4. Endereco (com confirmacao)
5. WhatsApp (com confirmacao)
6. Email (com confirmacao)
7. Horario preferencial (`Manha`/`Tarde`)
8. Fotos (uma ou multiplas)
9. Finalizacao e reset

## Observacoes de negocio atuais

- Nao ha etapa de selecao de estado geografico.
- Horario preferencial: somente `1 Manha` e `2 Tarde`.
