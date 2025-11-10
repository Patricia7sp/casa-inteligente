#!/usr/bin/env python3
"""
Teste da nova biblioteca TAPO
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integrations.tapo_client import TapoClient
from src.utils.config import settings

async def main():
    print("🧪 Testando nova biblioteca TAPO...")
    print(f"👤 Usuário: {settings.tapo_username}")
    print()
    
    client = TapoClient(settings.tapo_username, settings.tapo_password)
    
    # Testar com um IP específico (ajuste conforme necessário)
    test_ip = "192.168.68.108"  # IP de um dos seus dispositivos
    
    print(f"🔌 Testando conexão com {test_ip}...")
    
    success = await client.add_device(test_ip, "Teste")
    
    if success:
        print("✅ Conexão bem-sucedida!")
        print()
        
        # Obter informações
        info = await client.get_device_info("Teste")
        if info:
            print("📱 Informações do dispositivo:")
            print(f"   Modelo: {info['model']}")
            print(f"   MAC: {info['mac']}")
            print(f"   Firmware: {info['fw_ver']}")
            print(f"   Status: {'Ligado' if info['device_on'] else 'Desligado'}")
            print()
        
        # Obter dados de energia
        energy = await client.get_energy_usage("Teste")
        if energy:
            print("⚡ Dados de energia:")
            print(f"   Potência: {energy['power_watts']:.2f}W")
            print(f"   Energia hoje: {energy['energy_today_kwh']:.3f}kWh")
            print(f"   Status: {'Ligado' if energy['device_on'] else 'Desligado'}")
            print()
        
        print("🎉 Teste concluído com sucesso!")
    else:
        print("❌ Falha na conexão")
        print()
        print("💡 Dicas:")
        print("   - Verifique se o IP está correto")
        print("   - Confirme que está na mesma rede WiFi")
        print("   - Verifique usuário/senha no .env")

if __name__ == "__main__":
    asyncio.run(main())
