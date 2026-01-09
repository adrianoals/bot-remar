#!/usr/bin/env python3
"""
Script para testar a conexão com o Supabase
Verifica se as variáveis de ambiente estão configuradas e se a conexão funciona.
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def test_env_variables():
    """Testa se as variáveis de ambiente estão configuradas."""
    print("=" * 60)
    print("TESTE 1: Verificando Variáveis de Ambiente")
    print("=" * 60)
    
    required_vars = {
        "SUPABASE_URL": "URL do projeto Supabase",
        "SUPABASE_KEY": "Chave de API do Supabase"
    }
    
    missing_vars = []
    found_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value:
            missing_vars.append(var_name)
            print(f"❌ {var_name}: NÃO ENCONTRADA - {description}")
        else:
            # Mascarar a chave para segurança
            if "KEY" in var_name:
                masked_value = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
                print(f"✅ {var_name}: {masked_value} - {description}")
            else:
                print(f"✅ {var_name}: {value} - {description}")
            found_vars.append(var_name)
    
    print()
    if missing_vars:
        print(f"⚠️  Variáveis faltando: {', '.join(missing_vars)}")
        print("   Certifique-se de que o arquivo .env.local está configurado corretamente.")
        return False
    
    print("✅ Todas as variáveis de ambiente estão configuradas!")
    return True


def test_supabase_import():
    """Testa se o módulo supabase pode ser importado."""
    print("\n" + "=" * 60)
    print("TESTE 2: Verificando Importação do Módulo Supabase")
    print("=" * 60)
    
    try:
        from supabase import create_client, Client
        print("✅ Módulo supabase importado com sucesso!")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar módulo supabase: {e}")
        print("   Execute: pip install supabase")
        return False


def test_supabase_connection():
    """Testa a conexão real com o Supabase."""
    print("\n" + "=" * 60)
    print("TESTE 3: Testando Conexão com Supabase")
    print("=" * 60)
    
    try:
        from supabase import create_client
        from app.core.config import settings
        
        # Criar cliente
        print("📡 Criando cliente Supabase...")
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print("✅ Cliente criado com sucesso!")
        
        # Teste 1: Verificar se as tabelas existem
        print("\n📊 Testando acesso às tabelas...")
        
        # Teste tabela conversas
        try:
            print("   - Testando tabela 'conversas'...")
            response = client.table("conversas").select("wa_id").limit(1).execute()
            print(f"   ✅ Tabela 'conversas' acessível! (Encontrados {len(response.data)} registros)")
        except Exception as e:
            print(f"   ⚠️  Erro ao acessar tabela 'conversas': {e}")
            print("      (Isso é normal se a tabela ainda não foi criada)")
        
        # Teste tabela doacoes
        try:
            print("   - Testando tabela 'doacoes'...")
            response = client.table("doacoes").select("id").limit(1).execute()
            print(f"   ✅ Tabela 'doacoes' acessível! (Encontrados {len(response.data)} registros)")
        except Exception as e:
            print(f"   ⚠️  Erro ao acessar tabela 'doacoes': {e}")
            print("      (Isso é normal se a tabela ainda não foi criada)")
        
        # Teste 2: Verificar função RPC
        print("\n🔧 Testando função RPC 'get_ultima_doacao'...")
        try:
            # Testar com um wa_id fictício (não deve retornar erro, apenas vazio)
            response = client.rpc("get_ultima_doacao", {"wa_id_param": "+5511999999999"}).execute()
            print("   ✅ Função RPC 'get_ultima_doacao' acessível!")
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg.lower() or "function" in error_msg.lower():
                print(f"   ⚠️  Função RPC não encontrada: {e}")
                print("      (Execute o script database.sql para criar a função)")
            else:
                print(f"   ⚠️  Erro ao testar função RPC: {e}")
        
        # Teste 3: Verificar Storage
        print("\n📦 Testando acesso ao Storage...")
        try:
            buckets = client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            print(f"   ✅ Storage acessível! Buckets encontrados: {bucket_names}")
            
            if "whatsapp_media" in bucket_names:
                print("   ✅ Bucket 'whatsapp_media' encontrado!")
            else:
                print("   ⚠️  Bucket 'whatsapp_media' não encontrado")
                print("      (Crie o bucket seguindo o guia em docs/database/criar_storage_bucket.md)")
        except Exception as e:
            print(f"   ⚠️  Erro ao acessar Storage: {e}")
        
        print("\n✅ Conexão com Supabase estabelecida com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        print("\nPossíveis causas:")
        print("  1. SUPABASE_URL está incorreto")
        print("  2. SUPABASE_KEY está incorreto ou expirado")
        print("  3. Problemas de rede/firewall")
        print("  4. Projeto Supabase não existe ou foi deletado")
        return False


def test_supabase_service():
    """Testa o SupabaseService do projeto."""
    print("\n" + "=" * 60)
    print("TESTE 4: Testando SupabaseService")
    print("=" * 60)
    
    try:
        from app.services.supabase_service import SupabaseService
        
        print("📦 Criando instância do SupabaseService...")
        service = SupabaseService()
        print("✅ SupabaseService criado com sucesso!")
        
        # Teste básico
        print("\n🧪 Testando método get_user_state...")
        result = service.get_user_state("5511999999999")
        if result is None:
            print("   ✅ Método funcionando (nenhum registro encontrado, o que é esperado)")
        else:
            print(f"   ✅ Método funcionando (registro encontrado: {result})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar SupabaseService: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal que executa todos os testes."""
    print("\n" + "=" * 60)
    print("TESTE DE CONEXÃO COM SUPABASE")
    print("=" * 60)
    print()
    
    # Carregar variáveis de ambiente do .env.local ou .env
    from dotenv import load_dotenv
    
    env_file = root_dir / ".env.local"
    env_file_alt = root_dir / ".env"
    
    if env_file.exists():
        print(f"📄 Carregando variáveis de ambiente de: {env_file}")
        load_dotenv(env_file)
        print("✅ Arquivo .env.local carregado!")
    elif env_file_alt.exists():
        print(f"📄 Carregando variáveis de ambiente de: {env_file_alt}")
        load_dotenv(env_file_alt)
        print("✅ Arquivo .env carregado!")
    else:
        print(f"⚠️  Nenhum arquivo .env.local ou .env encontrado")
        print("   Usando apenas variáveis de ambiente do sistema")
    
    print()
    
    results = []
    
    # Teste 1: Variáveis de ambiente
    results.append(("Variáveis de Ambiente", test_env_variables()))
    
    # Teste 2: Importação do módulo
    results.append(("Importação do Módulo", test_supabase_import()))
    
    # Teste 3: Conexão (só se os anteriores passaram)
    if results[0][1] and results[1][1]:
        results.append(("Conexão com Supabase", test_supabase_connection()))
        results.append(("SupabaseService", test_supabase_service()))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print()
    if all_passed:
        print("🎉 Todos os testes passaram! Conexão com Supabase está funcionando.")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
