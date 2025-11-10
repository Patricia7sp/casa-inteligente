#!/usr/bin/env python3
"""
Listar todos os métodos disponíveis do dispositivo P110
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tapo import ApiClient
from src.utils.config import settings

async def main():
    print("🔍 Listando métodos disponíveis do P110...")
    print()
    
    client = ApiClient(settings.tapo_username, settings.tapo_password)
    device = await client.p110("192.168.68.108")
    
    print("📱 Métodos do dispositivo:")
    for method in dir(device):
        if not method.startswith('_') and callable(getattr(device, method)):
            print(f"   - {method}")
    
    print()
    print("🧪 Testando métodos de energia...")
    
    # Testar get_energy_usage
    try:
        energy = await device.get_energy_usage()
        print(f"✅ get_energy_usage(): {energy}")
    except Exception as e:
        print(f"❌ get_energy_usage(): {e}")
    
    # Testar se há get_current_power
    if hasattr(device, 'get_current_power'):
        try:
            power = await device.get_current_power()
            print(f"✅ get_current_power(): {power}")
        except Exception as e:
            print(f"❌ get_current_power(): {e}")
    else:
        print("⚠️  get_current_power() não existe")
    
    # Testar get_device_info
    try:
        info = await device.get_device_info()
        print(f"✅ get_device_info() - on_time: {info.on_time}s")
    except Exception as e:
        print(f"❌ get_device_info(): {e}")

if __name__ == "__main__":
    asyncio.run(main())
