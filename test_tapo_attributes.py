#!/usr/bin/env python3
"""
Descobrir atributos disponíveis na biblioteca tapo
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tapo import ApiClient
from src.utils.config import settings

async def main():
    print("🔍 Descobrindo atributos da biblioteca tapo...")
    print()
    
    client = ApiClient(settings.tapo_username, settings.tapo_password)
    device = await client.p110("192.168.68.108")
    
    # Device Info
    print("📱 DEVICE INFO:")
    info = await device.get_device_info()
    print(f"   Tipo: {type(info)}")
    print(f"   Atributos: {dir(info)}")
    print()
    for attr in dir(info):
        if not attr.startswith('_'):
            try:
                value = getattr(info, attr)
                if not callable(value):
                    print(f"   {attr}: {value}")
            except:
                pass
    
    print()
    print("⚡ ENERGY USAGE:")
    energy = await device.get_energy_usage()
    print(f"   Tipo: {type(energy)}")
    print(f"   Atributos: {dir(energy)}")
    print()
    for attr in dir(energy):
        if not attr.startswith('_'):
            try:
                value = getattr(energy, attr)
                if not callable(value):
                    print(f"   {attr}: {value}")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
