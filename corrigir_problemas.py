#!/usr/bin/env python3
"""
Script automático para corrigir os problemas identificados
"""
import subprocess
import sys
import os
from pathlib import Path


def check_postgresql():
    """Verificar e configurar PostgreSQL"""
    print("🗄️  VERIFICANDO POSTGRESQL...")
    
    try:
        # Verificar se PostgreSQL está rodando
        result = subprocess.run(['pg_isready'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL está rodando")
            return True
        else:
            print("❌ PostgreSQL não está rodando")
            print("📋 Execute os seguintes comandos:")
            print("   brew services start postgresql")
            print("   psql postgres -c 'CREATE USER postgres WITH PASSWORD \"casa_inteligente_2024\";'")
            print("   psql postgres -c 'CREATE DATABASE casa_inteligente OWNER postgres;'")
            print("   psql postgres -c 'GRANT ALL PRIVILEGES ON DATABASE casa_inteligente TO postgres;'")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL não instalado")
        print("📋 Instale com: brew install postgresql")
        return False


def check_env_file():
    """Verificar arquivo .env"""
    print("\n📝 VERIFICANDO ARQUIVO .ENV...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        return False
    
    # Ler arquivo .env
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Verificar credenciais TAPO
    if 'seu_email_tapo@exemplo.com' in content:
        print("❌ Credenciais TAPO não configuradas")
        print("📋 Edite o arquivo .env e substitua:")
        print("   TAPO_USERNAME=seu_email_real@exemplo.com")
        print("   TAPO_PASSWORD=sua_senha_real")
        return False
    else:
        print("✅ Credenciais TAPO parecem configuradas")
        return True


def check_dependencies():
    """Verificar dependências Python"""
    print("\n🐍 VERIFICANDO DEPENDÊNCIAS...")
    
    required_packages = [
        'sqlalchemy',
        'psycopg2-binary', 
        'pydantic-settings',
        'aiohttp',
        'pytapo'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📋 Instale pacotes faltantes:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_network():
    """Verificar conectividade com dispositivos"""
    print("\n🌐 VERIFICANDO REDE...")
    
    test_ips = ["192.168.68.110", "192.168.68.108"]
    online_devices = []
    
    for ip in test_ips:
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '2', ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {ip} online")
                online_devices.append(ip)
            else:
                print(f"❌ {ip} offline")
        except Exception:
            print(f"❌ {ip} erro")
    
    if online_devices:
        print(f"✅ {len(online_devices)} dispositivos online")
        return True
    else:
        print("❌ Nenhum dispositivo online")
        return False


def create_database_schema():
    """Criar esquema do banco"""
    print("\n🏗️  CRIANDO ESQUEMA DO BANCO...")
    
    try:
        sys.path.append('src')
        from models.database import create_tables
        
        create_tables()
        print("✅ Tabelas criadas/verificadas")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {str(e)}")
        return False


def run_diagnostics():
    """Executar diagnóstico completo"""
    print("\n🧪 EXECUTANDO DIAGNÓSTICO...")
    
    try:
        result = subprocess.run([sys.executable, 'diagnostico_simples.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Diagnóstico executado")
            print(result.stdout)
            return True
        else:
            print("❌ Erro no diagnóstico")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar diagnóstico: {str(e)}")
        return False


def main():
    """Função principal"""
    print("🛠️  SCRIPT DE CORREÇÃO AUTOMÁTICA")
    print("=" * 50)
    
    # Executar verificações
    checks = [
        ("Dependências Python", check_dependencies),
        ("Arquivo .env", check_env_file),
        ("PostgreSQL", check_postgresql),
        ("Rede Local", check_network),
    ]
    
    results = {}
    
    for name, check_func in checks:
        results[name] = check_func()
    
    # Resumo
    print("\n📊 RESUMO DAS VERIFICAÇÕES")
    print("=" * 50)
    
    all_ok = True
    for name, result in results.items():
        status = "✅ OK" if result else "❌ ERRO"
        print(f"{name}: {status}")
        if not result:
            all_ok = False
    
    # Criar esquema se banco estiver OK
    if results.get("PostgreSQL", False):
        create_database_schema()
    
    # Executar diagnóstico se tudo estiver OK
    if all_ok:
        print("\n🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
        print("📋 PRÓXIMOS PASSOS:")
        print("   1. Configure suas credenciais TAPO no .env")
        print("   2. Execute: python diagnostico_simples.py")
        print("   3. Inicie o sistema: docker-compose up -d")
        print("   4. Acesse: http://localhost:8501")
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS!")
        print("📋 CORRIJA OS ITENS ACIMA E EXECUTE NOVAMENTE:")
        print("   python corrigir_problemas.py")
    
    print("\n📖 Para ajuda detalhada, consulte: CORRECAO_PROBLEMAS.md")


if __name__ == "__main__":
    main()
