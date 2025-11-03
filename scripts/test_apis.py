#!/usr/bin/env python3
"""
Script para testar configurações das APIs TAPO e Nova Digital
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from integrations.tapo_client import TapoClient
from integrations.nova_digital_client import NovaDigitalClient
from utils.config import settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_tapo_connection():
    """Testar conexão com TAPO"""
    print("\n🔌 TESTANDO CONEXÃO TAPO")
    print("=" * 50)
    
    if not settings.tapo_username or not settings.tapo_password:
        print("❌ Credenciais TAPO não configuradas no .env")
        return False
    
    print(f"✅ Credenciais TAPO encontradas")
    print(f"   Usuario: {settings.tapo_username}")
    
    # Teste com IP comum (se existir)
    test_ips = ["192.168.1.100", "192.168.0.100", "192.168.1.101"]
    
    tapo_client = TapoClient(settings.tapo_username, settings.tapo_password)
    
    for ip in test_ips:
        print(f"\n🔍 Testando conexão com IP: {ip}")
        try:
            success = await tapo_client.add_device(ip, "test_device")
            if success:
                print(f"✅ Conexão TAPO bem-sucedida com {ip}")
                
                # Testar obtenção de dados
                energy_data = await tapo_client.get_energy_usage("test_device")
                if energy_data:
                    print(f"✅ Dados de energia obtidos: {energy_data}")
                else:
                    print("⚠️  Conectado mas não foi possível obter dados de energia")
                
                return True
            else:
                print(f"❌ Falha na conexão com {ip}")
        except Exception as e:
            print(f"❌ Erro ao conectar com {ip}: {str(e)}")
    
    print("\n💡 Dicas para configurar TAPO:")
    print("   1. Verifique se as tomadas estão na mesma rede")
    print("   2. Confirme suas credenciais TP-Link")
    print("   3. Use o app Tapo para encontrar os IPs corretos")
    print("   4. Teste um dispositivo por vez")
    
    return False


async def test_nova_digital_connection():
    """Testar conexão com Nova Digital"""
    print("\n🏠 TESTANDO CONEXÃO NOVA DIGITAL")
    print("=" * 50)
    
    if not settings.nova_digital_api_key:
        print("❌ API Key Nova Digital não configurada no .env")
        return False
    
    print(f"✅ API Key Nova Digital encontrada")
    print(f"   Base URL: {settings.nova_digital_base_url}")
    
    try:
        async with NovaDigitalClient(settings.nova_digital_api_key) as nova_client:
            print("\n🔍 Testando autenticação...")
            auth_success = await nova_client.authenticate()
            
            if auth_success:
                print("✅ Autenticação Nova Digital bem-sucedida")
                
                print("\n🔍 Obtendo lista de dispositivos...")
                devices = await nova_client.get_devices()
                
                if devices:
                    print(f"✅ Encontrados {len(devices)} dispositivos:")
                    for i, device in enumerate(devices[:3], 1):
                        print(f"   {i}. {device}")
                    
                    # Testar com primeiro dispositivo
                    if devices:
                        first_device = devices[0]
                        device_id = first_device.get('id', 'test_device')
                        
                        print(f"\n🔍 Testando obtenção de dados do dispositivo {device_id}...")
                        energy_data = await nova_client.get_energy_usage(device_id)
                        
                        if energy_data:
                            print(f"✅ Dados de energia obtidos: {energy_data}")
                        else:
                            print("⚠️  Conectado mas não foi possível obter dados de energia")
                    
                    return True
                else:
                    print("⚠️  Nenhum dispositivo encontrado no portal Nova Digital")
                    print("💡 Adicione seus dispositivos no portal Nova Digital primeiro")
                    return False
            else:
                print("❌ Falha na autenticação Nova Digital")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao conectar com Nova Digital: {str(e)}")
        print("\n💡 Dicas para configurar Nova Digital:")
        print("   1. Verifique se a API Key está correta")
        print("   2. Confirme se tem internet")
        print("   3. Verifique o status do portal Nova Digital")
        print("   4. Registre seus dispositivos no portal")
        
        return False


async def test_system_configuration():
    """Testar configuração geral do sistema"""
    print("\n🔧 TESTANDO CONFIGURAÇÃO DO SISTEMA")
    print("=" * 50)
    
    print(f"✅ App: {settings.app_name} v{settings.app_version}")
    print(f"✅ Debug: {settings.debug}")
    print(f"✅ Custo kWh: R$ {settings.energy_cost_per_kwh}")
    print(f"✅ Database URL: {settings.database_url}")
    print(f"✅ Redis URL: {settings.redis_url}")
    
    # Verificar configurações opcionais
    if settings.telegram_bot_token:
        print("✅ Telegram configurado")
    else:
        print("⚠️  Telegram não configurado (opcional)")
    
    if settings.email_username:
        print("✅ Email configurado")
    else:
        print("⚠️  Email não configurado (opcional)")
    
    if settings.openai_api_key:
        print("✅ OpenAI configurado")
    else:
        print("⚠️  OpenAI não configurado (opcional)")
    
    return True


async def main():
    """Função principal de testes"""
    print("🏠 CASA INTELIGENTE - TESTE DE CONFIGURAÇÕES")
    print("=" * 60)
    
    # Testar configuração do sistema
    system_ok = await test_system_configuration()
    
    # Testar TAPO
    tapo_ok = await test_tapo_connection()
    
    # Testar Nova Digital
    nova_ok = await test_nova_digital_connection()
    
    # Resumo final
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    print(f"✅ Sistema: {'OK' if system_ok else 'ERRO'}")
    print(f"✅ TAPO: {'OK' if tapo_ok else 'ERRO'}")
    print(f"✅ Nova Digital: {'OK' if nova_ok else 'ERRO'}")
    
    if system_ok and (tapo_ok or nova_ok):
        print("\n🎉 CONFIGURAÇÃO BÁSICA OK!")
        print("📋 Próximos passos:")
        print("   1. Inicie o sistema: docker-compose up -d")
        print("   2. Acesse: http://localhost:8000/docs")
        print("   3. Adicione seus dispositivos via API")
        print("   4. Monitore no dashboard: http://localhost:8501")
    else:
        print("\n❌ CONFIGURAÇÃO INCOMPLETA!")
        print("📋 Corrija os erros acima antes de prosseguir")
        print("📖 Consulte: docs/API_RESUMO.md")


if __name__ == "__main__":
    asyncio.run(main())
