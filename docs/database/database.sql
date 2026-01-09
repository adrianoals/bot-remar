-- ============================================================================
-- SCHEMA DO BANCO DE DADOS - CHATREMAR
-- Associação Remar do Brasil - Sistema de Chatbot WhatsApp
-- ============================================================================
-- Este arquivo contém o SQL completo para recriar todo o schema do projeto
-- Inclui: tabelas, índices, função RPC e instruções para Storage
-- ============================================================================

-- ============================================================================
-- TABELA: conversas
-- Propósito: Gerencia o estado atual da conversa de cada usuário
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversas (
    -- Chave primária: WhatsApp ID do usuário (número com +)
    wa_id VARCHAR(20) PRIMARY KEY,
    
    -- Estado atual da conversa no fluxo do chatbot
    -- Valores possíveis: inicio, inicio0, doacao, doacao_item_1 a doacao_item_9,
    -- acolhimento, lojas, servico, fretes
    estado VARCHAR(50) NOT NULL,
    
    -- Data da última interação (formato: YYYY-MM-DD)
    data DATE,
    
    -- Horário da última interação (formato: HH:MM:SS)
    horario TIME,
    
    -- Timestamp de criação do registro
    criado_em TIMESTAMP DEFAULT NOW()
);

-- Índices para otimização de consultas
CREATE UNIQUE INDEX IF NOT EXISTS idx_conversas_wa_id ON conversas(wa_id);
CREATE INDEX IF NOT EXISTS idx_conversas_estado ON conversas(estado);

-- Comentários nas colunas
COMMENT ON TABLE conversas IS 'Gerencia estados e dados temporários das conversas do chatbot';
COMMENT ON COLUMN conversas.wa_id IS 'WhatsApp ID do usuário (chave primária)';
COMMENT ON COLUMN conversas.estado IS 'Estado atual da conversa no fluxo do chatbot';
COMMENT ON COLUMN conversas.data IS 'Data da última interação';
COMMENT ON COLUMN conversas.horario IS 'Horário da última interação';
COMMENT ON COLUMN conversas.criado_em IS 'Timestamp de criação do registro';

-- ============================================================================
-- TABELA: doacoes
-- Propósito: Armazena dados completos das doações de itens
-- ============================================================================

CREATE TABLE IF NOT EXISTS doacoes (
    -- Chave primária: Identificador único da doação
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Alternativa para PostgreSQL sem UUID: usar SERIAL
    -- id SERIAL PRIMARY KEY,
    
    -- WhatsApp ID do doador (relacionamento com conversas)
    wa_id VARCHAR(20) NOT NULL,
    
    -- Categoria do item doado
    -- Valores possíveis: Móveis, Utensílios, Eletroeletrônicos, Roupas, Itens variados
    tipo_doacao VARCHAR(50) NOT NULL,
    
    -- Condição/estado do item doado
    -- Valores possíveis: Novo, Usado em bom estado, Usado com marcas de uso,
    -- Com defeito (ou misto: alguns bons, outros com defeito), Não sei dizer
    estado_doacao VARCHAR(100),
    
    -- Nome completo do responsável pela doação
    nome_responsavel VARCHAR(255),
    
    -- Endereço completo para retirada do item
    endereco_retirada TEXT,
    
    -- Número de WhatsApp para contato (pode ser diferente do wa_id)
    telefone_whatsapp VARCHAR(20),
    
    -- Email do responsável pela doação
    email VARCHAR(255),
    
    -- Horário preferencial para retirada
    -- Valores possíveis: Manhã, Tarde, Noite
    horario_preferencial VARCHAR(20),
    
    -- URLs ou caminhos das fotos do item (armazenadas no Supabase Storage)
    -- Pode ser: array de strings, JSONB, ou string separada por vírgulas
    fotos TEXT,
    -- Alternativa para múltiplas fotos: usar JSONB
    -- fotos JSONB,
    
    -- Timestamp de criação do registro
    criado_em TIMESTAMP DEFAULT NOW(),
    
    -- Timestamp da última atualização do registro
    atualizado_em TIMESTAMP DEFAULT NOW()
);

-- Índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_doacoes_wa_id ON doacoes(wa_id);
CREATE INDEX IF NOT EXISTS idx_doacoes_tipo ON doacoes(tipo_doacao);
CREATE INDEX IF NOT EXISTS idx_doacoes_criado_em ON doacoes(criado_em);

-- Comentários nas colunas
COMMENT ON TABLE doacoes IS 'Armazena dados completos das doações de itens realizadas pelos usuários';
COMMENT ON COLUMN doacoes.id IS 'Identificador único da doação (chave primária)';
COMMENT ON COLUMN doacoes.wa_id IS 'WhatsApp ID do doador';
COMMENT ON COLUMN doacoes.tipo_doacao IS 'Categoria do item doado';
COMMENT ON COLUMN doacoes.estado_doacao IS 'Condição/estado do item doado';
COMMENT ON COLUMN doacoes.nome_responsavel IS 'Nome completo do responsável pela doação';
COMMENT ON COLUMN doacoes.endereco_retirada IS 'Endereço completo para retirada do item';
COMMENT ON COLUMN doacoes.telefone_whatsapp IS 'Número de WhatsApp para contato';
COMMENT ON COLUMN doacoes.email IS 'Email do responsável pela doação';
COMMENT ON COLUMN doacoes.horario_preferencial IS 'Horário preferencial para retirada';
COMMENT ON COLUMN doacoes.fotos IS 'URLs ou caminhos das fotos do item (Supabase Storage)';
COMMENT ON COLUMN doacoes.criado_em IS 'Timestamp de criação do registro';
COMMENT ON COLUMN doacoes.atualizado_em IS 'Timestamp da última atualização do registro';

-- ============================================================================
-- TRIGGER: Atualizar campo atualizado_em automaticamente
-- ============================================================================

-- Função para atualizar o campo atualizado_em
CREATE OR REPLACE FUNCTION update_atualizado_em()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar atualizado_em na tabela doacoes
CREATE TRIGGER trigger_update_doacoes_atualizado_em
    BEFORE UPDATE ON doacoes
    FOR EACH ROW
    EXECUTE FUNCTION update_atualizado_em();

-- ============================================================================
-- FUNÇÃO RPC: get_ultima_doacao
-- Propósito: Buscar a última doação criada por um usuário específico
-- ============================================================================

-- Dropar a função existente (se houver) para evitar conflitos
DROP FUNCTION IF EXISTS get_ultima_doacao(TEXT);

-- Criar a função com os tipos corretos
CREATE OR REPLACE FUNCTION get_ultima_doacao(wa_id_param TEXT)
RETURNS TABLE (
    id UUID,
    wa_id VARCHAR(20),
    tipo_doacao VARCHAR(50),
    estado_doacao VARCHAR(100),
    nome_responsavel VARCHAR(255),
    endereco_retirada TEXT,
    telefone_whatsapp VARCHAR(20),
    email VARCHAR(255),
    horario_preferencial VARCHAR(20),
    fotos TEXT,
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.wa_id,
        d.tipo_doacao,
        d.estado_doacao,
        d.nome_responsavel,
        d.endereco_retirada,
        d.telefone_whatsapp,
        d.email,
        d.horario_preferencial,
        d.fotos,
        d.criado_em,
        d.atualizado_em
    FROM doacoes d
    WHERE d.wa_id = wa_id_param
    ORDER BY d.criado_em DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Comentário na função
COMMENT ON FUNCTION get_ultima_doacao(TEXT) IS 'Busca a última doação criada por um usuário específico, identificado pelo wa_id';

-- ============================================================================
-- CONSTRAINTS E VALIDAÇÕES
-- ============================================================================

-- Constraint para validar valores de tipo_doacao
ALTER TABLE doacoes
ADD CONSTRAINT check_tipo_doacao 
CHECK (tipo_doacao IN ('Móveis', 'Utensílios', 'Eletroeletrônicos', 'Roupas', 'Itens variados'));

-- Constraint para validar valores de estado_doacao
ALTER TABLE doacoes
ADD CONSTRAINT check_estado_doacao 
CHECK (estado_doacao IN (
    'Novo',
    'Usado em bom estado',
    'Usado com marcas de uso',
    'Com defeito (ou misto: alguns bons, outros com defeito)',
    'Não sei dizer'
) OR estado_doacao IS NULL);

-- Constraint para validar valores de horario_preferencial
ALTER TABLE doacoes
ADD CONSTRAINT check_horario_preferencial 
CHECK (horario_preferencial IN ('Manhã', 'Tarde', 'Noite') OR horario_preferencial IS NULL);

-- Constraint para validar formato básico de email (opcional, pode ser removido)
-- ALTER TABLE doacoes
-- ADD CONSTRAINT check_email_format 
-- CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- ============================================================================
-- DADOS INICIAIS (OPCIONAL)
-- ============================================================================

-- Inserir dados de exemplo (descomente se necessário)
-- INSERT INTO conversas (wa_id, estado, data, horario) 
-- VALUES ('+5511999999999', 'inicio', CURRENT_DATE, CURRENT_TIME)
-- ON CONFLICT (wa_id) DO NOTHING;

-- ============================================================================
-- SUPABASE STORAGE
-- ============================================================================
-- NOTA: O bucket do Supabase Storage não pode ser criado via SQL
-- É necessário criar manualmente através do Dashboard do Supabase ou API
-- 
-- Instruções:
-- 1. Acesse o Dashboard do Supabase
-- 2. Vá em Storage > Create a new bucket
-- 3. Nome do bucket: whatsapp_media
-- 4. Configurações:
--    - Public bucket: SIM (para acesso público às URLs)
--    - File size limit: Ajuste conforme necessário (ex: 10MB)
--    - Allowed MIME types: image/* (ou específicos: image/jpeg, image/png, etc.)
-- 5. Políticas de acesso:
--    - SELECT (read): Permitir acesso público
--    - INSERT (upload): Permitir apenas com autenticação (service_role key)
--    - UPDATE/DELETE: Conforme necessário
--
-- Ou via SQL (se habilitado):
-- INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
-- VALUES (
--     'whatsapp_media',
--     'whatsapp_media',
--     true,
--     10485760,  -- 10MB em bytes
--     ARRAY['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
-- );
-- ============================================================================

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - OPCIONAL
-- ============================================================================
-- Descomente e ajuste conforme necessário para segurança

-- Habilitar RLS nas tabelas
-- ALTER TABLE conversas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE doacoes ENABLE ROW LEVEL SECURITY;

-- Política para conversas: Permitir leitura/escrita apenas para usuários autenticados
-- CREATE POLICY "Conversas são acessíveis apenas para usuários autenticados"
-- ON conversas FOR ALL
-- USING (auth.role() = 'authenticated');

-- Política para doacoes: Permitir leitura/escrita apenas para usuários autenticados
-- CREATE POLICY "Doacoes são acessíveis apenas para usuários autenticados"
-- ON doacoes FOR ALL
-- USING (auth.role() = 'authenticated');

-- ============================================================================
-- VERIFICAÇÃO DO SCHEMA
-- ============================================================================

-- Verificar se as tabelas foram criadas
-- SELECT table_name 
-- FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name IN ('conversas', 'doacoes');

-- Verificar se a função foi criada
-- SELECT routine_name 
-- FROM information_schema.routines 
-- WHERE routine_schema = 'public' 
-- AND routine_name = 'get_ultima_doacao';

-- Verificar índices
-- SELECT indexname, tablename 
-- FROM pg_indexes 
-- WHERE schemaname = 'public' 
-- AND tablename IN ('conversas', 'doacoes');

-- ============================================================================
-- FIM DO SCRIPT
-- ============================================================================
