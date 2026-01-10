-- ============================================================================
-- ADICIONAR COLUNA mensagem_temp NA TABELA conversas
-- Propósito: Armazenar dados temporários durante o fluxo de conversação
-- ============================================================================

-- Adicionar coluna mensagem_temp para armazenar dados temporários
-- (nome, endereço, telefone, etc.) durante o fluxo
ALTER TABLE conversas 
ADD COLUMN IF NOT EXISTS mensagem_temp TEXT;

-- Comentário na coluna
COMMENT ON COLUMN conversas.mensagem_temp IS 'Armazena dados temporários durante o fluxo (nome, endereço, telefone, etc.)';
