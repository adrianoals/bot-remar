# Correção de erros no webhook MegaAPI e tabela conversas

## Título
Correção de erros relacionados ao webhook da MegaAPI e estrutura da tabela conversas

## Arquivos Modificados
- `app/flows/manager.py`
- `app/services/mega_api.py`
- `docs/database/database.sql`
- `docs/database/add_mensagem_temp_column.sql` (novo)

## Descrição Detalhada
Foram corrigidos dois erros críticos que impediam o funcionamento correto do chatbot:

1. **Erro na coluna 'nome'**: O código tentava salvar o campo `nome` na tabela `conversas`, mas essa coluna não existe. A tabela `conversas` só possui: `wa_id`, `estado`, `data`, `horario`, `criado_em`.

2. **Erro na coluna 'Mensagem'**: O código usava um campo `Mensagem` (com M maiúsculo) para armazenar dados temporários (nome, endereço, telefone, etc.) durante o fluxo, mas essa coluna também não existia na tabela.

3. **Erro na URL da MegaAPI**: Adicionada validação para garantir que `MEGA_API_URL` está configurada corretamente e tem o protocolo `http://` ou `https://`.

### Mudanças Realizadas

1. **Adicionada coluna `mensagem_temp` na tabela `conversas`**:
   - Tipo: `TEXT`
   - Propósito: Armazenar dados temporários durante o fluxo de conversação
   - Script SQL criado: `docs/database/add_mensagem_temp_column.sql`

2. **Atualizado `app/flows/manager.py`**:
   - Removida tentativa de salvar `nome` na tabela `conversas` (linha 128)
   - Substituídas todas as ocorrências de `Mensagem` por `mensagem_temp`
   - Corrigidos todos os pontos onde dados temporários são salvos/recuperados

3. **Melhorado `app/services/mega_api.py`**:
   - Adicionadas validações para `MEGA_API_URL`:
     - Verifica se está configurada
     - Verifica se começa com `http://` ou `https://`
   - Adicionada validação para `to_number` (não pode estar vazio)
   - Melhorados logs de erro para facilitar debug

4. **Atualizado `docs/database/database.sql`**:
   - Adicionada coluna `mensagem_temp` na definição da tabela `conversas`
   - Adicionado comentário explicativo na coluna

## Passo a Passo das Ações Realizadas

1. **Identificação dos erros**:
   - Erro: `Could not find the 'nome' column of 'conversas'`
   - Erro: `Could not find the 'Mensagem' column of 'conversas'`
   - Erro: `Request URL is missing an 'http://' or 'https://' protocol`

2. **Análise da estrutura da tabela**:
   - Verificado `docs/database/database.sql` e `docs/database/estrutura_tabelas.md`
   - Confirmado que `conversas` não possui colunas `nome` ou `Mensagem`

3. **Criação da solução**:
   - Criado script SQL para adicionar coluna `mensagem_temp`
   - Atualizado `database.sql` para incluir a nova coluna
   - Removida tentativa de salvar `nome` em `conversas`
   - Substituídas todas as referências de `Mensagem` por `mensagem_temp`

4. **Melhorias na validação**:
   - Adicionadas validações em `mega_api.py` para prevenir erros de URL
   - Melhorados logs de erro

## Critérios de Aceitação
- ✅ Coluna `mensagem_temp` adicionada à tabela `conversas`
- ✅ Código atualizado para usar `mensagem_temp` em vez de `Mensagem`
- ✅ Removida tentativa de salvar `nome` na tabela `conversas`
- ✅ Validações adicionadas para `MEGA_API_URL`
- ✅ Script SQL criado para aplicar a mudança em bancos existentes
- ✅ `database.sql` atualizado com a nova estrutura

## Status Final
✅ **Implementado** - Todas as correções foram aplicadas

## Observações
- **IMPORTANTE**: É necessário executar o script `add_mensagem_temp_column.sql` no Supabase para adicionar a coluna em bancos existentes
- A coluna `mensagem_temp` é usada apenas temporariamente durante o fluxo e não é persistida permanentemente
- Os dados finais são salvos na tabela `doacoes` quando o fluxo é concluído

## Como Aplicar

### Para bancos de dados existentes:
```sql
-- Execute no SQL Editor do Supabase:
ALTER TABLE conversas 
ADD COLUMN IF NOT EXISTS mensagem_temp TEXT;
```

### Para novos bancos:
- Use o arquivo `docs/database/database.sql` atualizado que já inclui a coluna
