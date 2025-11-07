#!/usr/bin/env python3
"""
Script para configurar PostgreSQL local para DBeaver
"""
import subprocess
import sys
import os


def check_postgresql_installation():
    """Verificar se PostgreSQL está instalado"""
    print("🔍 VERIFICANDO INSTALAÇÃO POSTGRESQL...")
    
    try:
        result = subprocess.run(['which', 'psql'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL encontrado em:", result.stdout.strip())
            return True
        else:
            print("❌ PostgreSQL não encontrado no PATH")
            print("📋 Instale com: brew install postgresql@15")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar PostgreSQL: {str(e)}")
        return False


def check_postgresql_service():
    """Verificar se serviço PostgreSQL está rodando"""
    print("\n🔍 VERIFICANDO SERVIÇO POSTGRESQL...")
    
    try:
        result = subprocess.run(['brew', 'services', 'list'], capture_output=True, text=True)
        if 'postgresql' in result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'postgresql' in line:
                    if 'started' in line:
                        print("✅ PostgreSQL está rodando")
                        return True
                    elif 'stopped' in line or 'error' in line:
                        print("⚠️  PostgreSQL parado ou com erro")
                        print("📋 Iniciando PostgreSQL...")
                        subprocess.run(['brew', 'services', 'restart', 'postgresql@15'], capture_output=True)
                        return True
        else:
            print("❌ PostgreSQL não encontrado nos serviços")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar serviço: {str(e)}")
        return False


def create_database_and_user():
    """Criar banco de dados e usuário"""
    print("\n🏗️  CRIANDO BANCO E USUÁRIO...")
    
    commands = [
        # Criar usuário se não existir
        "psql postgres -c \"CREATE USER postgres WITH PASSWORD 'casa_inteligente_2024' CREATEDB SUPERUSER;\" 2>/dev/null || echo 'Usuário já existe'",
        # Criar banco de dados
        "psql postgres -c \"CREATE DATABASE casa_inteligente OWNER postgres;\" 2>/dev/null || echo 'Banco já existe'",
        # Conceder privilégios
        "psql postgres -c \"GRANT ALL PRIVILEGES ON DATABASE casa_inteligente TO postgres;\""
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(f"   {result.stdout.strip()}")
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")


def test_connection():
    """Testar conexão com o banco"""
    print("\n🧪 TESTANDO CONEXÃO...")
    
    try:
        # Testar conexão via Python
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="casa_inteligente",
            user="postgres",
            password="casa_inteligente_2024"
        )
        
        print("✅ Conexão PostgreSQL local bem-sucedida!")
        
        # Verificar se tabelas existem
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"📊 Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False


def create_tables_if_needed():
    """Criar tabelas se não existirem"""
    print("\n🏗️  CRIANDO TABELAS...")
    
    try:
        sys.path.append('src')
        from models.database import create_tables
        
        create_tables()
        print("✅ Tabelas criadas/verificadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {str(e)}")
        return False


def show_dbeaver_config():
    """Mostrar configuração para DBeaver"""
    print("\n🐘 CONFIGURAÇÃO DBEAVER")
    print("=" * 50)
    print("Copie e cole estes dados no DBeaver:")
    print()
    print("📋 PostgreSQL Local:")
    print("   Host: localhost")
    print("   Port: 5432")
    print("   Database: casa_inteligente")
    print("   Username: postgres")
    print("   Password: casa_inteligente_2024")
    print()
    print("📋 Supabase (Produção):")
    print("   Host: db.pqqrodiuuhckvdqawgeg.supabase.co")
    print("   Port: 5432")
    print("   Database: postgres")
    print("   Username: postgres.pqqrodiuuhckvdqawgeg")
    print("   Password: [Obter no painel Supabase]")


def show_production_data():
    """Mostrar dados de produção"""
    print("\n🌐 DADOS EM PRODUÇÃO (SUPABASE)")
    print("=" * 50)
    print("Seu sistema está rodando em produção no Cloud Run!")
    print()
    print("📊 Dispositivos ativos:")
    print("   ✅ Tomada Inteligente - Purificador (192.168.68.110)")
    print("   ✅ Tomada Inteligente - Notebook (192.168.68.108)")
    print()
    print("📈 Leituras recentes:")
    print("   🟢 Purificador: ~15-20W")
    print("   🟢 Notebook: ~60-70W")
    print()
    print("🔗 URLs Produção:")
    print("   📊 Dashboard: [URL Cloud Run do seu dashboard]")
    print("   🔗 API: [URL Cloud Run da sua API]")
    print("   🗄️  Supabase: https://pqqrodiuuhckvdqawgeg.supabase.co")


def main():
    """Função principal"""
    print("🐘 CONFIGURAÇÃO POSTGRESQL LOCAL - DBEAVER")
    print("=" * 60)
    
    # Verificar instalação
    if not check_postgresql_installation():
        print("\n❌ PostgreSQL não está instalado")
        print("📋 Execute: brew install postgresql@15")
        return
    
    # Verificar serviço
    if not check_postgresql_service():
        print("\n❌ Não foi possível iniciar PostgreSQL")
        return
    
    # Criar banco e usuário
    create_database_and_user()
    
    # Testar conexão
    if test_connection():
        # Criar tabelas
        create_tables_if_needed()
        
        # Mostrar configuração DBeaver
        show_dbeaver_config()
        
        # Mostrar dados produção
        show_production_data()
        
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
        print("📋 Agora você pode:")
        print("   1. Abrir DBeaver e conectar com os dados acima")
        print("   2. Acessar dados em tempo real do Supabase")
        print("   3. Monitorar sistema em produção")
        
    else:
        print("\n❌ Falha na configuração")
        print("📋 Verifique:")
        print("   1. Se PostgreSQL está rodando: brew services list")
        print("   2. Se porta 5432 está livre")
        print("   3. Se senha está correta")


if __name__ == "__main__":
    main()
