#!/usr/bin/env python3
"""
Script completo de diagnóstico para conexão TAPO
"""
import asyncio
import logging
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from integrations.tapo_client import TapoClient
from integrations.tapo_cloud_client import TapoCloudClient
from utils.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_local_tapo():
    """Testar conexão local com dispositivos TAPO"""
    print("\n🔌 TESTANDO CONEXÃO LOCAL TAPO")
    print("=" * 60)
    
    if not settings.tapo_username or not settings.tapo_password:
        print("❌ Credenciais TAPO não configuradas no .env")
        print("   Por favor, edite o arquivo .env e preencha:")
        print("   TAPO_USERNAME=seu_email@exemplo.com")
        print("   TAPO_PASSWORD=sua_senha")
        return False
    
    print(f"✅ Credenciais encontradas: {settings.tapo_username}")
    
    # IPs dos dispositivos conhecidos
    test_devices = [
        {"name": "Purificador", "ip": "192.168.68.110"},
        {"name": "Notebook", "ip": "192.168.68.108"},
        {"name": "Geladeira", "ip": "192.168.1.100"},
    ]
    
    tapo_client = TapoClient(settings.tapo_username, settings.tapo_password)
    success_count = 0
    
    for device in test_devices:
        print(f"\n🔍 Testando dispositivo: {device['name']} ({device['ip']})")
        
        try:
            # Testar conexão
            connection_ok = await tapo_client.test_connection(device['ip'])
            
            if connection_ok:
                print(f"✅ Conexão bem-sucedida com {device['ip']}")
                
                # Adicionar dispositivo e testar leitura
                add_ok = await tapo_client.add_device(device['ip'], device['name'])
                
                if add_ok:
                    print(f"✅ Dispositivo {device['name']} adicionado")
                    
                    # Tentar obter dados de energia
                    energy_data = await tapo_client.get_energy_usage(device['name'])
                    
                    if energy_data:
                        print(f"✅ Dados de energia obtidos:")
                        print(f"   Potência: {energy_data['power_watts']:.2f}W")
                        print(f"   Voltagem: {energy_data['voltage']:.1f}V")
                        print(f"   Corrente: {energy_data['current']:.2f}A")
                        print(f"   Energia hoje: {energy_data['energy_today_kwh']:.3f}kWh")
                        success_count += 1
                    else:
                        print("⚠️  Conectado mas não foi possível obter dados de energia")
                        print("   O dispositivo pode não suportar monitoramento de energia")
                else:
                    print(f"❌ Falha ao adicionar dispositivo {device['name']}")
            else:
                print(f"❌ Falha na conexão com {device['ip']}")
                print("   Verifique se:")
                print("   - O dispositivo está online")
                print("   - O IP está correto")
                print("   - Está na mesma rede")
                print("   - As credenciais TAPO estão corretas")
                
        except Exception as e:
            print(f"❌ Erro ao testar {device['ip']}: {str(e)}")
    
    print(f"\n📊 Resumo: {success_count}/{len(test_devices)} dispositivos conectados")
    return success_count > 0


async def test_cloud_tapo():
    """Testar conexão via Cloud API TAPO"""
    print("\n☁️  TESTANDO CONEXÃO CLOUD TAPO")
    print("=" * 60)
    
    if not settings.tapo_username or not settings.tapo_password:
        print("❌ Credenciais TAPO não configuradas")
        return False
    
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


async def main():
    """Função principal de diagnóstico"""
    print("🏠 DIAGNÓSTICO COMPLETO - SISTEMA CASA INTELIGENTE")
    print("=" * 70)
    
    # Testar configurações
    print(f"✅ Configurações carregadas:")
    print(f"   TAPO User: {settings.tapo_username}")
    print(f"   Database: {settings.database_url[:50]}...")
    print(f"   Debug: {settings.debug}")
    
    # Executar testes
    db_ok = await test_database()
    local_ok = await test_local_tapo()
    cloud_ok = await test_cloud_tapo()
    
    # Resumo final
    print("\n📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    print(f"✅ Banco de Dados: {'OK' if db_ok else 'ERRO'}")
    print(f"✅ TAPO Local: {'OK' if local_ok else 'ERRO'}")
    print(f"✅ TAPO Cloud: {'OK' if cloud_ok else 'ERRO'}")
    
    # Recomendações
    print("\n🎯 RECOMENDAÇÕES:")
    if not db_ok:
        print("   1. Configure o PostgreSQL local")
    if not local_ok and not cloud_ok:
        print("   2. Configure suas credenciais TAPO no .env")
        print("   3. Verifique se seus dispositivos TAPO estão online")
    if local_ok:
        print("   4. Execute: python scripts/add_my_devices.py")
    if cloud_ok:
        print("   5. Use IDs da cloud para configuração")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("   1. Configure as credenciais no .env")
    print("   2. Execute este script novamente")
    print("   3. Inicie o sistema: docker-compose up -d")
    print("   4. Monitore em: http://localhost:8501")


if __name__ == "__main__":
    asyncio.run(main())
