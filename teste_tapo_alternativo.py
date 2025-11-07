#!/usr/bin/env python3
"""
Teste alternativo para conexão TAPO usando diferentes abordagens
"""
import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from utils.config import settings

async def test_kasa_library():
    """Testar usando biblioteca Kasa diretamente"""
    print("🔌 TESTANDO COM BIBLIOTECA KASA")
    print("=" * 50)
    
    try:
        from kasa import Discover, SmartPlug
        
        print("🔍 Procurando dispositivos Kasa/TP-Link na rede...")
        devices = await Discover.discover()
        
        if devices:
            print(f"✅ Encontrados {len(devices)} dispositivos:")
            for i, device in enumerate(devices, 1):
                print(f"\n--- Dispositivo {i} ---")
                print(f"  Host: {device.host}")
                print(f"  Alias: {device.alias}")
                print(f"  Modelo: {device.model}")
                print(f"  Estado: {'Ligado' if device.is_on else 'Desligado'}")
                
                # Tentar obter informações de energia
                try:
                    if hasattr(device, 'get_energy_usage'):
                        energy_info = await device.get_energy_usage()
                        print(f"  ⚡ Consumo: {energy_info.get('power', 0)}W")
                except:
                    print("  ⚠️  Sem informações de energia disponíveis")
                
                return True
        else:
            print("❌ Nenhum dispositivo Kasa encontrado")
            print("   Dicas:")
            print("   - Verifique se as tomadas estão na mesma rede")
            print("   - Tente especificar o IP diretamente")
            return False
            
    except ImportError:
        print("❌ Biblioteca Kasa não disponível")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar Kasa: {str(e)}")
        return False


async def test_direct_connection():
    """Testar conexão direta por IP"""
    print("\n🎯 TESTANDO CONEXÃO DIRETA POR IP")
    print("=" * 50)
    
    try:
        from kasa import SmartPlug
        
        test_ips = ["192.168.68.110", "192.168.68.108"]
        
        for ip in test_ips:
            print(f"\n🔍 Testando IP: {ip}")
            try:
                device = SmartPlug(ip)
                await device.update()
                
                print(f"✅ Dispositivo em {ip} conectado!")
                print(f"  Nome: {device.alias}")
                print(f"  Modelo: {device.model}")
                print(f"  Estado: {'Ligado' if device.is_on else 'Desligado'}")
                
                # Testar controle
                print("🔧 Testando controle...")
                if device.is_on:
                    await device.turn_off()
                    await asyncio.sleep(1)
                    await device.turn_on()
                    print("✅ Controle ligar/desligar funcionando!")
                else:
                    await device.turn_on()
                    await asyncio.sleep(1)
                    print("✅ Controle ligar funcionando!")
                
                # Testar energia se disponível
                if hasattr(device, 'get_energy_usage'):
                    try:
                        energy = await device.get_energy_usage()
                        print(f"⚡ Consumo atual: {energy.get('power', 0)}W")
                        print(f"📊 Energia hoje: {energy.get('today', 0)}kWh")
                    except:
                        print("⚠️  Monitoramento de energia não disponível")
                
                return True
                
            except Exception as e:
                print(f"❌ Erro ao conectar {ip}: {str(e)}")
        
        return False
        
    except ImportError:
        print("❌ Biblioteca Kasa não disponível")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False


async def test_tuya_cloud():
    """Testar conexão via Tuya Cloud (alternativa)"""
    print("\n☁️  TESTANDO TUYA CLOUD")
    print("=" * 50)
    
    if not settings.tuya_access_id or not settings.tuya_access_key:
        print("❌ Credenciais Tuya não configuradas")
        return False
    
    try:
        from src.integrations.tuya_cloud_client import TuyaCloudClient
        
        client = TuyaCloudClient(
            access_id=settings.tuya_access_id,
            access_key=settings.tuya_access_key,
            region=settings.tuya_region
        )
        
        print("🔍 Conectando à Tuya Cloud...")
        if await client.authenticate():
            print("✅ Autenticação Tuya bem-sucedida!")
            
            devices = await client.get_devices()
            if devices:
                print(f"📱 Encontrados {len(devices)} dispositivos:")
                for i, device in enumerate(devices, 1):
                    print(f"  {i}. {device.get('name', 'N/A')}")
                
                return True
            else:
                print("⚠️  Nenhum dispositivo encontrado na Tuya Cloud")
                return False
        else:
            print("❌ Falha na autenticação Tuya")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Tuya Cloud: {str(e)}")
        return False


async def main():
    """Função principal"""
    print("🏠 TESTE ALTERNATIVO - CONEXÃO TAPO/TUYA")
    print("=" * 60)
    
    print(f"✅ Configurações carregadas:")
    print(f"   TAPO User: {settings.tapo_username}")
    print(f"   Tuya ID: {settings.tuya_access_id}")
    
    # Executar testes
    kasa_ok = await test_kasa_library()
    direct_ok = await test_direct_connection()
    tuya_ok = await test_tuya_cloud()
    
    # Resumo
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    print(f"✅ Kasa Discovery: {'OK' if kasa_ok else 'ERRO'}")
    print(f"✅ Conexão Direta: {'OK' if direct_ok else 'ERRO'}")
    print(f"✅ Tuya Cloud: {'OK' if tuya_ok else 'ERRO'}")
    
    if kasa_ok or direct_ok or tuya_ok:
        print("\n🎉 PELO MENOS UMA CONEXÃO FUNCIONOU!")
        print("📋 PRÓXIMOS PASSOS:")
        print("   1. Adicione os dispositivos ao banco Supabase")
        print("   2. Configure o coletor de dados")
        print("   3. Inicie o sistema completo")
    else:
        print("\n❌ NENHUMA CONEXÃO FUNCIONOU")
        print("📋 VERIFIQUE:")
        print("   1. Se os dispositivos estão online")
        print("   2. Se estão na mesma rede")
        print("   3. As credenciais estão corretas")


if __name__ == "__main__":
    asyncio.run(main())
