"""
Script para testar a conexão com o Supabase e identificar problemas de autenticação.
Execute este script a partir da raiz do projeto:
    python -m tests.test_supabase_connection
"""

import os
import sys

# Adicionar o diretório pai ao path para poder importar do app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.supabase_client import SupabaseManager
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_supabase_connection():
    """Testa a conexão básica com o Supabase"""
    print("Testando a conexão com o Supabase...")
    
    # Verifique se o cliente foi inicializado corretamente
    if hasattr(SupabaseManager, 'client'):
        print("✓ Cliente Supabase inicializado")
    else:
        print("✗ Cliente Supabase NÃO inicializado")
        print("Verifique se as credenciais do Supabase estão configuradas corretamente")
        return False
    
    # Tenta acessar a tabela de usuários para verificar a conexão
    try:
        # Tente fazer uma consulta que não requer autenticação
        # Adapte isso de acordo com sua estrutura de dados
        result = SupabaseManager.client.table('profiles').select('id').limit(1).execute()
        print(f"✓ Consulta ao Supabase bem-sucedida")
        print(f"  Resposta: {result}")
        return True
    except Exception as e:
        print(f"✗ Erro ao acessar o Supabase: {str(e)}")
        print("Verifique suas credenciais e permissões de acesso")
        return False

def test_auth_endpoints():
    """Testa os endpoints de autenticação com o Supabase"""
    print("\nTestando endpoints de autenticação...")
    
    # Email e senha de teste
    test_email = input("Digite um email para teste (existente no sistema): ")
    test_password = input("Digite a senha: ")
    
    try:
        # Teste o login
        print(f"\nTestando login com {test_email}...")
        success, response = SupabaseManager.sign_in(test_email, test_password)
        
        if success:
            print("✓ Login bem-sucedido!")
            print(f"  Dados do usuário: {response.user.id if hasattr(response, 'user') else 'Estrutura de resposta diferente'}")
            print(f"  Resposta completa: {response.__dict__ if hasattr(response, '__dict__') else response}")
        else:
            print(f"✗ Falha no login: {response}")
            print("Possíveis causas:")
            print("  - Credenciais incorretas")
            print("  - Usuário não existe")
            print("  - Problemas com o Supabase")
        
        return success
    except Exception as e:
        print(f"✗ Erro ao testar autenticação: {str(e)}")
        import traceback
        print(f"  Detalhes: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TESTE DE CONEXÃO COM O SUPABASE")
    print("=" * 50)
    
    connection_success = test_supabase_connection()
    
    if connection_success:
        auth_success = test_auth_endpoints()
    else:
        print("\nNão é possível testar autenticação sem uma conexão válida com o Supabase.")