#!/usr/bin/env python3
"""
Script simplificado de diagnóstico para conexão TAPO
"""
import asyncio
import logging
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from integrations.tapo_cloud_client import TapoCloudClient
from utils.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_cloud_tapo():
    """Testar conexão via Cloud API TAPO"""
    print("\n☁️  TESTANDO CONEXÃO CLOUD TAPO")
    print("=" * 60)
    
    if not settings.tapo_username or not settings.tapo_password:
        print("❌ Credenciais TAPO não configuradas")
        print("   Por favor, edite o arquivo .env e preencha:")
        print("   TAPO_USERNAME=seu_email@exemplo.com")
        print("   TAPO_PASSWORD=sua_senha")
        return False
    
    print(f"✅ Credenciais encontradas: {settings.tapo_username}")
    
    try:
        async with TapoCloudClient(settings.tapo_username, settings.tapo_password) as client:
            print("🔍 Fazendo login na TP-Link Cloud...")
            
            login_ok = await client.login()
            
            if login_ok:
                print("✅ Login bem-sucedido na TP-Link Cloud")
                
                print("\n🔍 Buscando dispositivos na cloud...")
                devices = await client.get_device_list()
                
                if devices:
                    print(f"✅ Encontrados {len(devices)} dispositivos na cloud:")
                    
                    for i, device in enumerate(devices, 1):
                        print(f"\n--- Dispositivo {i} ---")
                        print(f"  Nome: {device.get('alias', 'N/A')}")
                        print(f"  ID: {device.get('deviceId', 'N/A')}")
                        print(f"  Modelo: {device.get('deviceModel', 'N/A')}")
                        print(f"  Tipo: {device.get('deviceType', 'N/A')}")
                        print(f"  MAC: {device.get('deviceMac', 'N/A')}")
                        print(f"  Status: {device.get('status', 'N/A')}")
                        
                        # Testar dados de energia
                        device_id = device.get('deviceId')
                        if device_id:
                            energy = await client.get_energy_usage(device_id)
                            if energy:
                                print(f"  ⚡ Potência: {energy.get('power_watts', 0)}W")
                                print(f"  📊 Energia hoje: {energy.get('energy_today_kwh', 0)}kWh")
                    
                    return True
                else:
                    print("⚠️  Nenhum dispositivo encontrado na cloud")
                    print("   Verifique se seus dispositivos estão vinculados à sua conta TP-Link")
                    return False
            else:
                print("❌ Falha no login na TP-Link Cloud")
                print("   Verifique suas credenciais")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar conexão cloud: {str(e)}")
        return False


async def test_database():
    """Testar conexão com banco de dados"""
    print("\n💾 TESTANDO CONEXÃO BANCO DE DADOS")
    print("=" * 60)
    
    try:
        from models.database import get_db, Device, create_tables
        
        print("🔍 Testando conexão PostgreSQL...")
        
        # Criar tabelas se não existirem
        create_tables()
        print("✅ Tabelas verificadas/criadas")
        
        # Listar dispositivos cadastrados
        db = next(get_db())
        devices = db.query(Device).all()
        db.close()
        
        if devices:
            print(f"✅ Encontrados {len(devices)} dispositivos no banco:")
            for device in devices:
                print(f"  - {device.name} ({device.type}) - {device.ip_address}")
                print(f"    Local: {device.location} | Equipamento: {device.equipment_connected}")
        else:
            print("⚠️  Nenhum dispositivo cadastrado no banco")
            print("   Execute: python scripts/add_my_devices.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {str(e)}")
        print("   Verifique se PostgreSQL está rodando")
        print("   Verifique a string de conexão no .env")
        return False


async def test_local_connection():
    """Testar conexão local básica"""
    print("\n🔌 TESTANDO CONEXÃO LOCAL")
    print("=" * 60)
    
    test_ips = ["192.168.68.110", "192.168.68.108", "192.168.1.100"]
    
    for ip in test_ips:
        print(f"\n🔍 Testando ping para {ip}...")
        try:
            import subprocess
            result = subprocess.run(['ping', '-c', '1', '-W', '2', ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {ip} respondeu ao ping")
            else:
                print(f"❌ {ip} não respondeu ao ping")
        except Exception as e:
            print(f"❌ Erro ao pingar {ip}: {str(e)}")
    
    return True


async def main():
    """Função principal de diagnóstico"""
    print("🏠 DIAGNÓSTICO CASA INTELIGENTE - VERSÃO SIMPLIFICADA")
    print("=" * 70)
    
    # Testar configurações
    print(f"✅ Configurações carregadas:")
    print(f"   TAPO User: {settings.tapo_username}")
    print(f"   Database: {settings.database_url[:50]}...")
    print(f"   Debug: {settings.debug}")
    
    # Executar testes
    local_ok = await test_local_connection()
    db_ok = await test_database()
    cloud_ok = await test_cloud_tapo()
    
    # Resumo final
    print("\n📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    print(f"✅ Rede Local: {'OK' if local_ok else 'ERRO'}")
    print(f"✅ Banco de Dados: {'OK' if db_ok else 'ERRO'}")
    print(f"✅ TAPO Cloud: {'OK' if cloud_ok else 'ERRO'}")
    
    # Análise do problema
    print("\n🔍 ANÁLISE DO PROBLEMA:")
    if not cloud_ok:
        print("   ❌ PROBLEMA IDENTIFICADO: Credenciais TAPO não configuradas ou inválidas")
        print("   📋 SOLUÇÃO:")
        print("      1. Abra o arquivo .env")
        print("      2. Preencha TAPO_USERNAME com seu email TP-Link")
        print("      3. Preencha TAPO_PASSWORD com sua senha TP-Link")
        print("      4. Execute este script novamente")
    
    if not db_ok:
        print("   ❌ PROBLEMA: Banco de dados PostgreSQL não acessível")
        print("   📋 SOLUÇÃO:")
        print("      1. Verifique se PostgreSQL está rodando")
        print("      2. Verifique a string DATABASE_URL no .env")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    if cloud_ok and db_ok:
        print("   1. Execute: python scripts/add_my_devices.py")
        print("   2. Inicie o sistema: docker-compose up -d")
        print("   3. Acesse o dashboard: http://localhost:8501")
    else:
        print("   1. Corrija os problemas identificados acima")
        print("   2. Execute este diagnóstico novamente")
        print("   3. Continue com a configuração quando tudo estiver OK")


if __name__ == "__main__":
    asyncio.run(main())
