-- Controle global de automação do bot
-- ativo_global = true  -> bot responde normalmente
-- ativo_global = false -> bot ignora mensagens de usuários

CREATE TABLE IF NOT EXISTS public.automacao_controle (
    id SMALLINT PRIMARY KEY,
    ativo_global BOOLEAN NOT NULL DEFAULT TRUE,
    atualizado_em TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO public.automacao_controle (id, ativo_global, atualizado_em)
VALUES (1, TRUE, NOW())
ON CONFLICT (id) DO NOTHING;
