# Scripts de Teste

Este diretório contém scripts úteis para testar e validar o sistema.

## 📋 Scripts Disponíveis

### `test_supabase_connection.py`

Script para testar a conexão com o Supabase e verificar se tudo está configurado corretamente.

#### Como usar:

```bash
# Opção 1: Executar diretamente
python3 scripts/test_supabase_connection.py

# Opção 2: Tornar executável e rodar
chmod +x scripts/test_supabase_connection.py
./scripts/test_supabase_connection.py
```

#### O que o script testa:

1. ✅ **Variáveis de Ambiente**: Verifica se `SUPABASE_URL` e `SUPABASE_KEY` estão configuradas
2. ✅ **Importação do Módulo**: Verifica se o módulo `supabase` está instalado
3. ✅ **Conexão com Supabase**: Testa a conexão real com o banco de dados
4. ✅ **Acesso às Tabelas**: Verifica se as tabelas `conversas` e `doacoes` existem
5. ✅ **Função RPC**: Testa se a função `get_ultima_doacao` está disponível
6. ✅ **Storage**: Verifica se o bucket `whatsapp_media` existe
7. ✅ **SupabaseService**: Testa a classe de serviço do projeto

#### Requisitos:

- Python 3.7+
- Variáveis de ambiente configuradas (`.env.local` ou `.env`)
- Dependências instaladas: `pip install -r requirements.txt`

#### Exemplo de saída:

```
============================================================
TESTE DE CONEXÃO COM SUPABASE
============================================================

📄 Carregando variáveis de ambiente de: /path/to/.env.local
✅ Arquivo .env.local carregado!

============================================================
TESTE 1: Verificando Variáveis de Ambiente
============================================================
✅ SUPABASE_URL: https://xxxxx.supabase.co - URL do projeto Supabase
✅ SUPABASE_KEY: eyJhbGciOi...xxxx - Chave de API do Supabase
✅ Todas as variáveis de ambiente estão configuradas!

============================================================
TESTE 2: Verificando Importação do Módulo Supabase
============================================================
✅ Módulo supabase importado com sucesso!

============================================================
TESTE 3: Testando Conexão com Supabase
============================================================
📡 Criando cliente Supabase...
✅ Cliente criado com sucesso!

📊 Testando acesso às tabelas...
   - Testando tabela 'conversas'...
   ✅ Tabela 'conversas' acessível! (Encontrados 0 registros)
   - Testando tabela 'doacoes'...
   ✅ Tabela 'doacoes' acessível! (Encontrados 0 registros)

🔧 Testando função RPC 'get_ultima_doacao'...
   ✅ Função RPC 'get_ultima_doacao' acessível!

📦 Testando acesso ao Storage...
   ✅ Storage acessível! Buckets encontrados: ['whatsapp_media']
   ✅ Bucket 'whatsapp_media' encontrado!

✅ Conexão com Supabase estabelecida com sucesso!

============================================================
RESUMO DOS TESTES
============================================================
✅ PASSOU - Variáveis de Ambiente
✅ PASSOU - Importação do Módulo
✅ PASSOU - Conexão com Supabase
✅ PASSOU - SupabaseService

🎉 Todos os testes passaram! Conexão com Supabase está funcionando.
```

#### Troubleshooting:

**Erro: "Variáveis de ambiente não encontradas"**
- Certifique-se de que o arquivo `.env.local` existe na raiz do projeto
- Verifique se as variáveis estão nomeadas corretamente: `SUPABASE_URL` e `SUPABASE_KEY`

**Erro: "ModuleNotFoundError: No module named 'supabase'"**
- Instale as dependências: `pip install -r requirements.txt`

**Erro: "Erro ao conectar com Supabase"**
- Verifique se `SUPABASE_URL` está correto (formato: `https://xxxxx.supabase.co`)
- Verifique se `SUPABASE_KEY` está correto (chave `service_role` ou `anon`)
- Verifique sua conexão com a internet
- Verifique se o projeto Supabase existe e está ativo

**Erro: "Tabela não encontrada"**
- Execute o script `docs/database/database.sql` no SQL Editor do Supabase

**Erro: "Bucket não encontrado"**
- Siga o guia em `docs/database/criar_storage_bucket.md` para criar o bucket
