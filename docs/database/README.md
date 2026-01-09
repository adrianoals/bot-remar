# Documentação do Banco de Dados - ChatRemar

Este diretório contém a documentação completa sobre a estrutura de dados do sistema ChatRemar.

## 📄 Documentos Disponíveis

### [estrutura_tabelas.md](./estrutura_tabelas.md)
Documentação completa e detalhada sobre:
- Tabela `conversas` - Estados e dados temporários das conversas
- Tabela `doacoes` - Dados completos das doações
- Função RPC `get_ultima_doacao`
- Supabase Storage (bucket `whatsapp_media`)
- Scripts SQL de criação
- Relacionamentos entre tabelas

### [database.sql](./database.sql)
Script SQL completo para recriar todo o schema do projeto:
- Criação das tabelas `conversas` e `doacoes`
- Índices para otimização
- Função RPC `get_ultima_doacao`
- Triggers para atualização automática
- Constraints e validações
- Instruções para criação do bucket de Storage
- Comentários e documentação inline

### [criar_storage_bucket.md](./criar_storage_bucket.md)
Guia completo para criar o bucket `whatsapp_media` no Supabase Storage:
- Método 1: Via Dashboard (recomendado)
- Método 2: Via SQL Editor
- Método 3: Via API REST (programático)
- Configurações de segurança
- Políticas de acesso
- Troubleshooting

### [storage_policies.sql](./storage_policies.sql)
Script SQL com políticas de acesso para o bucket `whatsapp_media`:
- Política de leitura pública
- Política de upload (apenas autenticados)
- Política de atualização (apenas autenticados)
- Política de deleção (apenas autenticados)
- Alternativa com política única para service_role

## 🗄️ Resumo Rápido

### Tabelas Principais

1. **`conversas`**
   - Gerencia estados das conversas
   - Campos: `wa_id`, `estado`, `data`, `horario`, `criado_em`
   - Chave primária: `wa_id`

2. **`doacoes`**
   - Armazena dados das doações de itens
   - Campos: `id`, `wa_id`, `tipo_doacao`, `estado_doacao`, `nome_responsavel`, `endereco_retirada`, `telefone_whatsapp`, `email`, `horario_preferencial`, `fotos`, `criado_em`, `atualizado_em`
   - Chave primária: `id`

### Recursos Adicionais

- **Função RPC**: `get_ultima_doacao(wa_id_param TEXT)`
- **Storage**: Bucket `whatsapp_media` para fotos

## 🔗 Relacionamento

```
conversas (wa_id) ──> (1:N) ──> doacoes (wa_id)
```

Um usuário pode ter múltiplas doações, mas apenas uma conversa ativa.

## 📊 Estatísticas

- **Total de Tabelas**: 2
- **Total de Campos**: 17 (5 em `conversas` + 12 em `doacoes`)
- **Funções RPC**: 1
- **Buckets de Storage**: 1

## 🚀 Próximos Passos

1. Revisar a documentação completa em [estrutura_tabelas.md](./estrutura_tabelas.md)
2. Executar os scripts SQL de criação
3. Configurar políticas de acesso e RLS
4. Testar todas as operações
